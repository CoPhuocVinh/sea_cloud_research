package vn.younet.wordcloud;

import org.apache.lucene.analysis.Tokenizer;
import org.apache.lucene.analysis.icu.segmentation.ICUTokenizer;
import org.apache.lucene.analysis.tokenattributes.CharTermAttribute;
import org.apache.lucene.analysis.tokenattributes.OffsetAttribute;
import org.apache.lucene.analysis.tokenattributes.PositionIncrementAttribute;
import org.apache.lucene.analysis.tokenattributes.TypeAttribute;
import org.apache.lucene.util.AttributeFactory;

import java.io.IOException;
import java.io.StringReader;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.regex.Matcher;

/**
 * Một tokenizer cho mọi nước SEA, chọn cách tách theo hệ chữ chứ không theo nước:
 * đoạn chữ Thái đi qua {@link ThaiSegmenter}, phần còn lại (Latin, Hán, emoji, số) đi qua ICU.
 *
 * <p>Ranh giới câu/mệnh đề ({@code . ! ? ; : , …} xuống dòng, hashtag/URL/@mention đã bỏ, và dấu cách
 * nằm giữa hai chữ Thái) được đánh dấu bằng position increment = 2 ở token đầu đoạn mới, để
 * {@link CloudPhraseFilter} không ghép cụm vượt ranh giới (BR-29).
 *
 * <p>{@code emitHashtags}: phát mỗi hashtag thành 1 token type {@value #TYPE_HASHTAG} (giữ dấu {@code #}), để
 * wordcloud dạng copyField + TextField vẫn có hashtag (BR-31) trong cùng trường; tắt thì hashtag chỉ là ranh giới.
 */
public final class ScriptRoutingTokenizer extends Tokenizer {
    public static final String TYPE_THAI = "<THAI>";
    public static final String TYPE_HASHTAG = "<HASHTAG>";
    private static final int SEGMENT_GAP = 2;

    private final CharTermAttribute termAtt = addAttribute(CharTermAttribute.class);
    private final OffsetAttribute offsetAtt = addAttribute(OffsetAttribute.class);
    private final TypeAttribute typeAtt = addAttribute(TypeAttribute.class);
    private final PositionIncrementAttribute posIncAtt = addAttribute(PositionIncrementAttribute.class);

    private final ThaiSegmenter thaiSegmenter;
    private final boolean emitHashtags;
    private final ICUTokenizer icu = new ICUTokenizer();
    private Iterator<Token> tokens;
    private int finalOffset;

    public ScriptRoutingTokenizer(AttributeFactory factory, ThaiSegmenter thaiSegmenter, boolean emitHashtags) {
        super(factory);
        this.thaiSegmenter = thaiSegmenter;
        this.emitHashtags = emitHashtags;
    }

    @Override
    public boolean incrementToken() throws IOException {
        if (tokens == null) {
            tokens = tokenize(readAll()).iterator();
        }
        if (!tokens.hasNext()) {
            return false;
        }
        clearAttributes();
        Token t = tokens.next();
        termAtt.append(t.term);
        offsetAtt.setOffset(correctOffset(t.start), correctOffset(t.end));
        typeAtt.setType(t.type);
        posIncAtt.setPositionIncrement(t.posInc);
        return true;
    }

    private String readAll() throws IOException {
        StringBuilder sb = new StringBuilder();
        char[] buf = new char[4096];
        int n;
        while ((n = input.read(buf)) != -1) {
            sb.append(buf, 0, n);
        }
        finalOffset = sb.length();
        return sb.toString();
    }

    private List<Token> tokenize(String text) throws IOException {
        char[] chars = text.toCharArray();
        boolean[] boundary = markBoundaries(text, chars);
        int[] hashtagEnd = emitHashtags ? hashtagEnds(text) : null;
        List<Token> out = new ArrayList<>();
        boolean newSegment = false;
        int i = 0;
        while (i < chars.length) {
            if (hashtagEnd != null && hashtagEnd[i] > 0) {
                Token tag = new Token(text.substring(i, hashtagEnd[i]), i, hashtagEnd[i], TYPE_HASHTAG);
                tag.posInc = out.isEmpty() ? 1 : SEGMENT_GAP;
                out.add(tag);
                newSegment = true;
                i = hashtagEnd[i];
                continue;
            }
            if (boundary[i]) {
                newSegment = true;
                i++;
                continue;
            }
            int end = i;
            boolean thai = ThaiSegmenter.isThai(chars[i]);
            while (end < chars.length && !boundary[end] && ThaiSegmenter.isThai(chars[end]) == thai) {
                end++;
            }
            int before = out.size();
            if (thai) {
                addThai(text.substring(i, end), i, out);
            } else {
                addIcu(text.substring(i, end), i, out);
            }
            if (newSegment && out.size() > before && before > 0) {
                out.get(before).posInc = SEGMENT_GAP;
            }
            if (out.size() > before) {
                newSegment = false;
            }
            i = end;
        }
        return out;
    }

    /** {@code ends[start]} = vị trí kết thúc của hashtag bắt đầu tại {@code start}, 0 nếu không có. */
    private static int[] hashtagEnds(String text) {
        int[] ends = new int[text.length()];
        for (int[] span : CloudPatterns.hashtagSpans(text)) {
            ends[span[0]] = span[1];
        }
        return ends;
    }

    private static boolean[] markBoundaries(String text, char[] chars) {
        boolean[] boundary = new boolean[chars.length];
        Matcher m = CloudPatterns.SKIPPED.matcher(text);
        while (m.find()) {
            for (int k = m.start(); k < m.end(); k++) {
                boundary[k] = true;
            }
        }
        for (int k = 0; k < chars.length; k++) {
            if (isBoundaryChar(chars, k)) {
                boundary[k] = true;
            }
        }
        markThaiSpaces(chars, boundary);
        return boundary;
    }

    private static boolean isBoundaryChar(char[] c, int k) {
        switch (c[k]) {
            case '\n': case '\r': case '!': case '?': case ';': case '…': case '|':
            case '。': case '！': case '？':
                return true;
            case '.': case ',': case ':':
                // 10.10, 10,000, 12:30 không phải ranh giới
                return !(k > 0 && k + 1 < c.length && Character.isDigit(c[k - 1]) && Character.isDigit(c[k + 1]));
            default:
                return false;
        }
    }

    /** Dấu cách (kể cả NBSP) giữa hai chữ Thái là ranh giới cụm/mệnh đề trong tiếng Thái. Một lượt O(n). */
    private static void markThaiSpaces(char[] c, boolean[] boundary) {
        int k = 0;
        while (k < c.length) {
            if (!isSpace(c[k])) {
                k++;
                continue;
            }
            int end = k;
            while (end < c.length && isSpace(c[end])) {
                end++;
            }
            if (k > 0 && end < c.length && ThaiSegmenter.isThai(c[k - 1]) && ThaiSegmenter.isThai(c[end])) {
                for (int s = k; s < end; s++) {
                    boundary[s] = true;
                }
            }
            k = end;
        }
    }

    private static boolean isSpace(char c) {
        return Character.isWhitespace(c) || Character.isSpaceChar(c);
    }

    private void addThai(String run, int base, List<Token> out) {
        for (ThaiSegmenter.Word w : thaiSegmenter.tokenize(run)) {
            out.add(new Token(w.term, base + w.start, base + w.end, TYPE_THAI));
        }
    }

    private void addIcu(String run, int base, List<Token> out) throws IOException {
        icu.setReader(new StringReader(run));
        CharTermAttribute term = icu.getAttribute(CharTermAttribute.class);
        OffsetAttribute off = icu.getAttribute(OffsetAttribute.class);
        TypeAttribute type = icu.getAttribute(TypeAttribute.class);
        icu.reset();
        try {
            while (icu.incrementToken()) {
                out.add(new Token(term.toString(), base + off.startOffset(), base + off.endOffset(), type.type()));
            }
            icu.end();
        } finally {
            icu.close();
        }
    }

    @Override
    public void end() throws IOException {
        super.end();
        int offset = correctOffset(finalOffset);
        offsetAtt.setOffset(offset, offset);
    }

    @Override
    public void reset() throws IOException {
        super.reset();
        tokens = null;
        finalOffset = 0;
    }

    private static final class Token {
        final String term;
        final int start;
        final int end;
        final String type;
        int posInc = 1;

        Token(String term, int start, int end, String type) {
            this.term = term;
            this.start = start;
            this.end = end;
            this.type = type;
        }
    }
}
