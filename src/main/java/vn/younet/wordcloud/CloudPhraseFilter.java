package vn.younet.wordcloud;

import org.apache.lucene.analysis.CharArraySet;
import org.apache.lucene.analysis.TokenFilter;
import org.apache.lucene.analysis.TokenStream;
import org.apache.lucene.analysis.tokenattributes.CharTermAttribute;
import org.apache.lucene.analysis.tokenattributes.OffsetAttribute;
import org.apache.lucene.analysis.tokenattributes.PositionIncrementAttribute;
import org.apache.lucene.analysis.tokenattributes.TypeAttribute;

import java.io.IOException;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;
import java.util.Locale;
import java.util.Set;

/**
 * Sinh cụm wordcloud từ token đã chuẩn hoá, theo từng đoạn câu (position increment &gt; 1 là ranh giới):
 * <ol>
 *   <li>gộp cụm có trong gazetteer thành 1 đơn vị, khớp dài nhất (cùng ý với {@code PhraseMerger} bên
 *       vncore_nlp_research), nên tên riêng không bị cắt dù viết hoa hay thường;</li>
 *   <li>ghép các đơn vị liền nhau thành cụm {@code minWords..maxWords} từ, bỏ cụm mở đầu hoặc kết thúc
 *       bằng stopword hoặc token không có chữ cái (BR-30); cụm gazetteer luôn được giữ; từ trong
 *       {@code tailWords} (từ nhấn mạnh: banget, talaga, เพราะ) được phép đứng cuối dù là stopword;</li>
 *   <li>chữ Thái ghép bằng {@link #THAI_JOINER} (dấu cách vô hình U+200B: người đọc thấy viết liền, nhưng bước
 *       làm sạch và gazetteer vẫn biết ranh giới từ), còn lại ghép bằng 1 dấu cách.</li>
 * </ol>
 * Chỉ phát ra cụm (type {@value #TYPE_PHRASE}), không phát ra từ đơn; token hashtag (nếu tokenizer bật
 * {@code emitHashtags}) được phát nguyên, là ranh giới cụm. Nếu có {@code vocabulary} (từ vựng cụm
 * đã đào trước theo topic) thì chỉ giữ cụm có trong đó, để số giá trị phân biệt trong docValues không bùng nổ.
 */
public final class CloudPhraseFilter extends TokenFilter {
    public static final String TYPE_PHRASE = "PHRASE";
    /** Nối 2 từ Thái trong cụm: zero-width space, không hiện ra và cũng là điểm ngắt dòng chuẩn của tiếng Thái. */
    public static final char THAI_JOINER = '\u200B';
    /** Cụm dài hơn mức này là rác (token vô nghĩa rất dài); cũng giữ term dưới giới hạn 32766 byte. */
    static final int MAX_PHRASE_CHARS = 120;

    private final CharTermAttribute termAtt = addAttribute(CharTermAttribute.class);
    private final OffsetAttribute offsetAtt = addAttribute(OffsetAttribute.class);
    private final TypeAttribute typeAtt = addAttribute(TypeAttribute.class);
    private final PositionIncrementAttribute posIncAtt = addAttribute(PositionIncrementAttribute.class);

    private final Set<String> gazetteer;
    private final int maxGazetteerTokens;
    private final CharArraySet edgeStopwords;
    private final CharArraySet tailWords;
    private final Set<String> vocabulary;
    private final int minWords;
    private final int maxWords;

    private final Deque<Phrase> output = new ArrayDeque<>();
    private final List<Unit> segment = new ArrayList<>();
    private Unit carried;
    /** Hashtag kết thúc đoạn hiện tại: phát SAU các cụm của đoạn để offset không lùi (IndexWriter bắt buộc). */
    private Phrase pendingHashtag;
    private boolean exhausted;

    public CloudPhraseFilter(TokenStream input, Set<String> gazetteer, int maxGazetteerTokens,
                             CharArraySet edgeStopwords, CharArraySet tailWords, Set<String> vocabulary,
                             int minWords, int maxWords) {
        super(input);
        this.gazetteer = gazetteer;
        this.maxGazetteerTokens = maxGazetteerTokens;
        this.edgeStopwords = edgeStopwords;
        this.tailWords = tailWords;
        this.vocabulary = vocabulary;
        this.minWords = minWords;
        this.maxWords = maxWords;
    }

    @Override
    public boolean incrementToken() throws IOException {
        while (output.isEmpty()) {
            if (exhausted) {
                return false;
            }
            fillSegment();
            emitSegment();
            if (pendingHashtag != null) {
                output.add(pendingHashtag);
                pendingHashtag = null;
            }
        }
        Phrase p = output.poll();
        clearAttributes();
        termAtt.append(p.text);
        offsetAtt.setOffset(p.start, p.end);
        typeAtt.setType(TYPE_PHRASE);
        posIncAtt.setPositionIncrement(1);
        return true;
    }

    /** Đọc token tới hết đoạn câu hiện tại; token đầu đoạn kế tiếp được giữ lại trong {@code carried}. */
    private void fillSegment() throws IOException {
        segment.clear();
        if (carried != null) {
            segment.add(carried);
            carried = null;
        }
        while (input.incrementToken()) {
            int posInc = posIncAtt.getPositionIncrement();
            if (posInc == 0) {
                continue; // token xếp chồng (synonym): chỉ giữ token đầu
            }
            if (ScriptRoutingTokenizer.TYPE_HASHTAG.equals(typeAtt.type())) {
                pendingHashtag = new Phrase(termAtt.toString(), offsetAtt.startOffset(), offsetAtt.endOffset());
                return;
            }
            Unit unit = new Unit(termAtt.toString(), offsetAtt.startOffset(), offsetAtt.endOffset());
            if (posInc > 1 && !segment.isEmpty()) {
                carried = unit;
                return;
            }
            segment.add(unit);
        }
        exhausted = true;
    }

    private void emitSegment() {
        List<Unit> units = mergeGazetteer(segment);
        for (int i = 0; i < units.size(); i++) {
            Unit first = units.get(i);
            if (first.gazetteer) {
                emit(first.text, first.start, first.end, true);
            }
            if (!isEdge(first)) {
                continue;
            }
            StringBuilder text = new StringBuilder(first.text);
            int words = first.words;
            for (int j = i + 1; j < units.size(); j++) {
                Unit last = units.get(j);
                words += last.words;
                if (words > maxWords) {
                    break;
                }
                append(text, last.text);
                if (words >= minWords && (isEdge(last) || tailWords.contains(last.text))) {
                    emit(text.toString(), first.start, last.end, false);
                }
            }
        }
    }

    private void emit(String text, int start, int end, boolean fromGazetteer) {
        boolean known = fromGazetteer || vocabulary.isEmpty() || vocabulary.contains(text);
        if (known && text.length() <= MAX_PHRASE_CHARS) {
            output.add(new Phrase(text, start, end));
        }
    }

    private List<Unit> mergeGazetteer(List<Unit> tokens) {
        if (gazetteer.isEmpty()) {
            return tokens;
        }
        List<Unit> units = new ArrayList<>(tokens.size());
        int i = 0;
        while (i < tokens.size()) {
            int bestEnd = i;
            StringBuilder key = new StringBuilder(tokens.get(i).text);
            for (int j = i + 1; j < tokens.size() && j - i < maxGazetteerTokens; j++) {
                append(key, tokens.get(j).text);
                if (gazetteer.contains(key.toString())) {
                    bestEnd = j;
                }
            }
            if (bestEnd > i) {
                units.add(join(tokens.subList(i, bestEnd + 1)));
                i = bestEnd + 1;
            } else {
                units.add(tokens.get(i));
                i++;
            }
        }
        return units;
    }

    private static Unit join(List<Unit> parts) {
        StringBuilder text = new StringBuilder(parts.get(0).text);
        for (int k = 1; k < parts.size(); k++) {
            append(text, parts.get(k).text);
        }
        Unit unit = new Unit(text.toString(), parts.get(0).start, parts.get(parts.size() - 1).end);
        unit.words = parts.size();
        unit.gazetteer = true;
        return unit;
    }

    /** Chữ Thái liền chữ Thái thì nối bằng {@link #THAI_JOINER}, còn lại cách nhau 1 dấu cách. */
    static void append(StringBuilder sb, String next) {
        boolean thaiJoin = sb.length() > 0 && ThaiSegmenter.isThai(sb.charAt(sb.length() - 1))
                && !next.isEmpty() && ThaiSegmenter.isThai(next.charAt(0));
        sb.append(thaiJoin ? THAI_JOINER : ' ').append(next);
    }

    /**
     * Chuẩn hoá 1 dòng gazetteer/từ vựng về đúng dạng filter tạo ra: lowercase, khoảng trắng gộp thành 1, và khoảng
     * trắng (hoặc U+200B) giữa 2 chữ Thái thành {@link #THAI_JOINER}. Nhờ vậy gazetteer Thái viết
     * {@code "ลิซ่า แบล็กพิงก์"} khớp được cụm {@code ลิซ่า}+{@code แบล็กพิงก์}.
     */
    static String normalizeEntry(String line) {
        String collapsed = line.trim().toLowerCase(Locale.ROOT).replaceAll("[\\s\\u200B]+", " ");
        return collapsed.replaceAll("(?<=[\\u0E00-\\u0E7F]) (?=[\\u0E00-\\u0E7F])", String.valueOf(THAI_JOINER));
    }

    /** Số từ của 1 dòng đã chuẩn hoá (tách theo dấu cách và {@link #THAI_JOINER}). */
    static int countWords(String entry) {
        return entry.isEmpty() ? 0 : entry.split("[ \\u200B]").length;
    }

    private boolean isEdge(Unit unit) {
        return unit.gazetteer || (hasLetter(unit.text) && !edgeStopwords.contains(unit.text));
    }

    private static boolean hasLetter(String text) {
        for (int i = 0; i < text.length(); i++) {
            if (Character.isLetter(text.charAt(i))) {
                return true;
            }
        }
        return false;
    }

    @Override
    public void reset() throws IOException {
        super.reset();
        output.clear();
        segment.clear();
        carried = null;
        pendingHashtag = null;
        exhausted = false;
    }

    private static final class Unit {
        final String text;
        final int start;
        final int end;
        int words = 1;
        boolean gazetteer;

        Unit(String text, int start, int end) {
            this.text = text;
            this.start = start;
            this.end = end;
        }
    }

    private static final class Phrase {
        final String text;
        final int start;
        final int end;

        Phrase(String text, int start, int end) {
            this.text = text;
            this.start = start;
            this.end = end;
        }
    }
}
