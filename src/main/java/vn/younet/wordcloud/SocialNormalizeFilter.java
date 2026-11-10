package vn.younet.wordcloud;

import org.apache.lucene.analysis.TokenFilter;
import org.apache.lucene.analysis.TokenStream;
import org.apache.lucene.analysis.tokenattributes.CharTermAttribute;
import org.apache.lucene.analysis.tokenattributes.PositionIncrementAttribute;
import org.apache.lucene.analysis.tokenattributes.TypeAttribute;

import java.io.IOException;
import java.util.Map;
import java.util.regex.Matcher;

/**
 * Chuẩn hoá token mạng xã hội (chạy sau khi đã lowercase):
 * <ul>
 *   <li>bỏ emoji và tiếng cười ({@code wkwkwk}, {@code 55555}, {@code hahaha}) và coi chỗ đó là ranh giới;</li>
 *   <li>dấu nháy cong {@code ’ ʼ} thành {@code '} (để khớp stoplist, vd. {@code don’t});</li>
 *   <li>chữ Latin lặp từ 3 lần trở lên: ở cuối từ còn 1 ({@code bangetttt} thành {@code banget}),
 *       ở giữa từ còn 2 ({@code goooood} thành {@code good});</li>
 *   <li>láy bằng số 2 thành 2 token ({@code jalan2} thành {@code jalan jalan}), trừ
 *       {@link CloudPatterns#NOT_REDUPLICATION} ({@code part2}, {@code season2});</li>
 *   <li>bỏ sở hữu cách {@code 's} ({@code singapore's} thành {@code singapore});</li>
 *   <li>slang/viết tắt thành dạng chuẩn theo bảng 1 từ -&gt; 1 từ ({@code gak} thành {@code tidak}).</li>
 * </ul>
 * Không dùng SynonymGraphFilter cho slang vì filter đó đặt lại position increment của token được thay,
 * làm mất ranh giới câu mà tokenizer đã đánh dấu.
 */
public final class SocialNormalizeFilter extends TokenFilter {
    private static final String TYPE_EMOJI = "<EMOJI>";

    private final CharTermAttribute termAtt = addAttribute(CharTermAttribute.class);
    private final TypeAttribute typeAtt = addAttribute(TypeAttribute.class);
    private final PositionIncrementAttribute posIncAtt = addAttribute(PositionIncrementAttribute.class);

    private final Map<String, String> slang;
    /** Bản sao thứ 2 của token láy; phải capture vì filter phía sau dùng chung attribute. */
    private State pendingCopy;

    public SocialNormalizeFilter(TokenStream input, Map<String, String> slang) {
        super(input);
        this.slang = slang;
    }

    @Override
    public boolean incrementToken() throws IOException {
        if (pendingCopy != null) {
            restoreState(pendingCopy);
            posIncAtt.setPositionIncrement(1);
            pendingCopy = null;
            return true;
        }
        int dropped = 0;
        while (input.incrementToken()) {
            String term = termAtt.toString();
            if (TYPE_EMOJI.equals(typeAtt.type()) || CloudPatterns.LAUGHTER.matcher(term).matches()) {
                dropped += posIncAtt.getPositionIncrement();
                continue;
            }
            if (dropped > 0) {
                posIncAtt.setPositionIncrement(posIncAtt.getPositionIncrement() + dropped);
            }
            normalize(term);
            return true;
        }
        return false;
    }

    private void normalize(String term) {
        String type = typeAtt.type();
        if (ScriptRoutingTokenizer.TYPE_THAI.equals(type) || ScriptRoutingTokenizer.TYPE_HASHTAG.equals(type)) {
            return;
        }
        String t = collapseElongation(term.replace('’', '\'').replace('ʼ', '\''));
        if (t.endsWith("'s")) {
            t = t.substring(0, t.length() - 2);
        }
        Matcher m = CloudPatterns.DIGIT_REDUPLICATION.matcher(t);
        boolean reduplicated = m.matches() && !CloudPatterns.NOT_REDUPLICATION.contains(m.group(1));
        if (reduplicated) {
            t = m.group(1);
        }
        t = slang.getOrDefault(t, t);
        if (!t.equals(term)) {
            termAtt.setEmpty().append(t);
        }
        if (reduplicated) {
            pendingCopy = captureState();
        }
    }

    static String collapseElongation(String term) {
        StringBuilder out = new StringBuilder(term.length());
        int i = 0;
        while (i < term.length()) {
            char c = term.charAt(i);
            int j = i;
            while (j < term.length() && term.charAt(j) == c) {
                j++;
            }
            int run = j - i;
            boolean atEnd = j == term.length();
            int keep = Character.isLetter(c) && run >= 3 ? (atEnd ? 1 : 2) : run;
            for (int k = 0; k < keep; k++) {
                out.append(c);
            }
            i = j;
        }
        return out.toString();
    }

    @Override
    public void reset() throws IOException {
        super.reset();
        pendingCopy = null;
    }
}
