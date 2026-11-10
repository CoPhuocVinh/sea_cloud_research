package vn.younet.wordcloud;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Các mẫu regex dùng chung cho tokenizer, filter và update processor (một nguồn duy nhất). */
public final class CloudPatterns {
    /**
     * Hashtag kể cả dấu kết hợp (dấu thanh tiếng Thái, dấu tiếng Việt). Phải có ít nhất 1 chữ cái và không đứng
     * ngay sau {@code &} (loại HTML entity {@code &#39;}). Hashtag dính liền {@code #A#B} vẫn tách được 2.
     * {@code #fragment} trong URL được loại bằng cách bỏ URL trước khi quét.
     */
    public static final Pattern HASHTAG = Pattern.compile("(?<!&)#(?=[\\p{N}_]*\\p{L})[\\p{L}\\p{M}\\p{N}_]+");
    /** Hashtag dài hơn mức này là rác (và tránh vượt giới hạn 32766 byte của term). */
    public static final int MAX_HASHTAG_CHARS = 100;
    public static final Pattern URL = Pattern.compile("(?i)\\b(?:https?://|www\\.)\\S+");
    public static final Pattern MENTION = Pattern.compile("@[\\p{L}\\p{M}\\p{N}_.]+");
    /** Chuỗi literal "\n", "\r", "\t" còn sót trong data export (vd. {@code \ncảm}). */
    public static final Pattern ESCAPED_NEWLINE = Pattern.compile("\\\\[nrt]");
    /** Mọi vùng bị bỏ khỏi văn bản và coi như ranh giới câu. */
    public static final Pattern SKIPPED = Pattern.compile(
            HASHTAG.pattern() + "|" + URL.pattern() + "|" + MENTION.pattern() + "|" + ESCAPED_NEWLINE.pattern());

    /** Tiếng cười: wkwk (id), haha/hehe/hihi, 555 (th), kkk, lol. */
    public static final Pattern LAUGHTER = Pattern.compile(
            "(?:w?k(?:wk)+w?|(?:ha){2,}h?|(?:he){2,}|(?:hi){2,}|5{3,}|k{3,}|lo+l+)");
    /** Láy bằng số 2: jalan2, main2, lucu2 (id/ms). */
    public static final Pattern DIGIT_REDUPLICATION = Pattern.compile("(\\p{L}{2,})2");
    /** Từ hay đi kèm số 2 nhưng không phải láy (part2, season2, gen2…). */
    public static final Set<String> NOT_REDUPLICATION = Set.of(
            "part", "season", "gen", "ep", "eps", "episode", "vol", "chapter", "chap", "round", "day", "week",
            "level", "lv", "lvl", "stage", "phase", "ver", "version", "game", "top", "team", "group", "book",
            "player", "mv", "ss", "ps", "galaxy", "iphone", "pro", "max", "plus", "mini", "note");

    private CloudPatterns() {
    }

    /**
     * Vị trí [start, end) các hashtag trong văn bản: bỏ {@code #fragment} nằm trong URL và hashtag dài quá
     * {@link #MAX_HASHTAG_CHARS}. Dùng chung cho tokenizer và update processor.
     */
    public static List<int[]> hashtagSpans(String text) {
        Matcher url = URL.matcher(text);
        StringBuilder masked = new StringBuilder(text);
        while (url.find()) {
            for (int k = url.start(); k < url.end(); k++) {
                masked.setCharAt(k, ' ');
            }
        }
        List<int[]> spans = new ArrayList<>();
        Matcher m = HASHTAG.matcher(masked);
        while (m.find()) {
            if (m.end() - m.start() <= MAX_HASHTAG_CHARS) {
                spans.add(new int[]{m.start(), m.end()});
            }
        }
        return spans;
    }
}
