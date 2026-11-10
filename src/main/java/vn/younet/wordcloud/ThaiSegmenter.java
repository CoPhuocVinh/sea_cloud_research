package vn.younet.wordcloud;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Tách từ tiếng Thái kiểu maximal matching (giống tinh thần {@code newmm} của PyThaiNLP):
 * quy hoạch động chọn cách tách ít cụm không có trong từ điển nhất, rồi ít token nhất.
 * Không bao giờ cắt giữa một cụm ký tự (phụ âm + dấu/nguyên âm đi kèm + đuôi câm {@code ์}), nên không còn
 * kiểu vỡ {@code ซาด้|า} như ICU hay {@code วิ|ชญ์}. Các cụm không có trong từ điển liền nhau được gộp thành 1 token.
 * {@link #tokenize} thêm phần xử lý chữ kéo dài của mạng xã hội.
 */
public final class ThaiSegmenter {
    /** Từ điển mặc định: words_th.txt của PyThaiNLP (CC0-1.0). */
    public static final String DEFAULT_DICTIONARY = "words_th.txt";
    private static final char MAIYAMOK = 'ๆ';
    private static final char THANTHAKHAT = '์';
    static final int MAX_CLUSTER_CHARS = 8;
    static final int MAX_TOKEN_CHARS = 30;

    private final Node root = new Node();
    private int maxWordLength;

    private ThaiSegmenter() {
    }

    public static ThaiSegmenter withDefaultDictionary() throws IOException {
        ThaiSegmenter segmenter = new ThaiSegmenter();
        try (InputStream in = ThaiSegmenter.class.getResourceAsStream(DEFAULT_DICTIONARY)) {
            if (in == null) {
                throw new IOException("Missing bundled resource " + DEFAULT_DICTIONARY);
            }
            segmenter.addAll(readLines(in));
        }
        return segmenter;
    }

    public ThaiSegmenter addAll(Collection<String> words) {
        for (String word : words) {
            String w = word.trim();
            if (!w.isEmpty() && !w.startsWith("#")) {
                add(w);
            }
        }
        return this;
    }

    private void add(String word) {
        Node node = root;
        for (int i = 0; i < word.length(); i++) {
            node = node.children.computeIfAbsent(word.charAt(i), c -> new Node());
        }
        node.terminal = true;
        maxWordLength = Math.max(maxWordLength, word.length());
    }

    /** Thai block U+0E00–U+0E7F. */
    public static boolean isThai(char c) {
        return c >= '฀' && c <= '๿';
    }

    static boolean isConsonant(char c) {
        return c >= 'ก' && c <= 'ฮ';
    }

    static boolean isThaiDigit(char c) {
        return c >= '๐' && c <= '๙';
    }

    /** Dấu và nguyên âm không thể đứng đầu một từ (phải đi sau phụ âm). */
    static boolean isNonStarter(char c) {
        return (c >= 'ะ' && c <= 'ฺ') || c == 'ๅ' || (c >= '็' && c <= '๎');
    }

    /** Nguyên âm đứng trước phụ âm (เ แ โ ใ ไ): không thể kết thúc một từ. */
    static boolean isLeadingVowel(char c) {
        return c >= 'เ' && c <= 'ไ';
    }

    /** Một từ Thái đã tách: chữ (đã rút ký tự kéo dài) và vị trí [start, end) trong chuỗi gốc. */
    public static final class Word {
        public final String term;
        public final int start;
        public final int end;

        Word(String term, int start, int end) {
            this.term = term;
            this.start = start;
            this.end = end;
        }
    }

    /**
     * Tách một đoạn chỉ gồm chữ Thái của bài đăng mạng xã hội:
     * <ul>
     *   <li>chữ lặp từ 3 lần ({@code มากกกก}, trừ chữ số) rút còn 1 nhưng được dùng chung: từ trước kết thúc bằng nó và từ sau
     *       có thể bắt đầu bằng nó ({@code ขึ้นนนนี้} thành {@code ขึ้น} + {@code นี้});</li>
     *   <li>dấu/nguyên âm đi sau lặp từ 2 lần ({@code เยอะะ}) và {@code ๆ} lặp rút còn 1;</li>
     *   <li>một ký tự lẻ giống ký tự cuối của từ ngay trước ({@code สายย}, {@code แล้วว}) được gộp vào từ đó.</li>
     * </ul>
     */
    public List<Word> tokenize(String run) {
        Collapsed c = collapse(run);
        List<int[]> spans = segment(c.text, c.doubleable);
        List<Word> words = new ArrayList<>(spans.size());
        int prevEnd = -1;
        for (int k = 0; k < spans.size(); k++) {
            int[] span = spans.get(k);
            int s = span[0];
            int e = span[1];
            boolean sharedStart = span[2] == 1;
            boolean sharedEnd = k + 1 < spans.size() && spans.get(k + 1)[2] == 1;
            int start = sharedStart ? c.end[s] - 1 : c.start[s];
            int end = sharedEnd ? c.end[e - 1] - 1 : c.end[e - 1];
            if (isElongationTail(c.text, s, e, sharedStart, prevEnd)) {
                Word prev = words.remove(words.size() - 1);
                words.add(new Word(prev.term, prev.start, end));
            } else {
                words.add(new Word(c.text.substring(s, e), start, end));
            }
            prevEnd = e;
        }
        return words;
    }

    private static boolean isElongationTail(String text, int s, int e, boolean sharedStart, int prevEnd) {
        return e - s == 1 && !sharedStart && prevEnd == s && s > 0 && isConsonant(text.charAt(s))
                && text.charAt(s) == text.charAt(s - 1);
    }

    /** Chuỗi đã rút ký tự kéo dài; ký tự thứ k đại diện cho [start[k], end[k]) của chuỗi gốc. */
    static final class Collapsed {
        final String text;
        final int[] start;
        final int[] end;
        final boolean[] doubleable;

        Collapsed(String text, int[] start, int[] end, boolean[] doubleable) {
            this.text = text;
            this.start = start;
            this.end = end;
            this.doubleable = doubleable;
        }
    }

    static Collapsed collapse(String text) {
        StringBuilder out = new StringBuilder(text.length());
        int[] start = new int[text.length()];
        int[] end = new int[text.length()];
        boolean[] doubleable = new boolean[text.length()];
        int i = 0;
        while (i < text.length()) {
            char c = text.charAt(i);
            int j = i;
            while (j < text.length() && text.charAt(j) == c) {
                j++;
            }
            int run = j - i;
            if (c == MAIYAMOK || (run >= 3 && !isThaiDigit(c)) || (run == 2 && isNonStarter(c))) {
                int k = out.length();
                out.append(c);
                start[k] = i;
                end[k] = j;
                doubleable[k] = run >= 3 && isConsonant(c);
            } else {
                for (int r = 0; r < run; r++) {
                    int k = out.length();
                    out.append(c);
                    start[k] = i + r;
                    end[k] = i + r + 1;
                }
            }
            i = j;
        }
        return new Collapsed(out.toString(), start, end, doubleable);
    }

    /**
     * Tách chuỗi chỉ gồm ký tự Thái; trả về các khoảng {start, end, 0} theo vị trí trong {@code text}.
     */
    public List<int[]> segment(String text) {
        return segment(text, null);
    }

    /**
     * {@code doubleable[k]}: ký tự k là phụ âm kéo dài đã rút, được dùng chung cho từ kết thúc tại nó và từ
     * bắt đầu tại nó. Khoảng trả về {start, end, 1} nghĩa là token bắt đầu bằng ký tự dùng chung với token trước.
     */
    private List<int[]> segment(String text, boolean[] doubleable) {
        int n = text.length();
        int[] unknown = new int[n + 1];
        int[] tokens = new int[n + 1];
        int[] next = new int[n + 1];
        boolean[] known = new boolean[n + 1];
        boolean[] shared = new boolean[n + 1];
        int[] nextStarter = nextStarters(text);
        for (int i = n - 1; i >= 0; i--) {
            int clusterEnd = clusterEnd(text, i, nextStarter);
            unknown[i] = unknown[clusterEnd] + 1;
            tokens[i] = tokens[clusterEnd] + 1;
            next[i] = clusterEnd;
            Node node = root;
            for (int j = i; j < n && j - i < maxWordLength; j++) {
                node = node.children.get(text.charAt(j));
                if (node == null) {
                    break;
                }
                if (!node.terminal) {
                    continue;
                }
                int end = j + 1;
                if (isValidEnd(text, end) && better(unknown[end], tokens[end] + 1, unknown[i], tokens[i])) {
                    unknown[i] = unknown[end];
                    tokens[i] = tokens[end] + 1;
                    next[i] = end;
                    known[i] = true;
                    shared[i] = false;
                }
                // Hoà điểm thì ưu tiên dùng chung: chữ kéo dài thuộc về cuối từ trước (มากกกว่า -> มาก + กว่า, không phải มา + กว่า)
                if (doubleable != null && doubleable[j] && j > i && karanTailEnd(text, j) == j
                        && !better(unknown[i], tokens[i], unknown[j], tokens[j] + 1)) {
                    unknown[i] = unknown[j];
                    tokens[i] = tokens[j] + 1;
                    next[i] = j;
                    known[i] = true;
                    shared[i] = true;
                }
            }
        }
        return mergeUnknown(text, next, known, shared);
    }

    private static boolean better(int unknownA, int tokensA, int unknownB, int tokensB) {
        return unknownA < unknownB || (unknownA == unknownB && tokensA < tokensB);
    }

    private static boolean isValidEnd(String text, int end) {
        return !isLeadingVowel(text.charAt(end - 1))
                && (end == text.length() || (!isNonStarter(text.charAt(end)) && karanTailEnd(text, end) == end));
    }

    /**
     * Đuôi câm của luật TCC (PyThaiNLP): 1–2 phụ âm, có thể kèm {@code ิ}/{@code ุ}, kết thúc bằng {@code ์}
     * ({@code ต์}, {@code ชญ์}, {@code นต์}, {@code ทร์}). Đuôi này luôn thuộc cụm đứng trước.
     * Trả về vị trí sau đuôi bắt đầu tại {@code p}, hoặc {@code p} nếu không có đuôi.
     */
    private static int karanTailEnd(String text, int p) {
        int n = text.length();
        if (p >= n || !isConsonant(text.charAt(p))) {
            return p;
        }
        int k = p + 1;
        if (k < n && isConsonant(text.charAt(k))) {
            k++;
        }
        if (k < n && (text.charAt(k) == 'ิ' || text.charAt(k) == 'ุ')) {
            k++;
        }
        return k < n && text.charAt(k) == THANTHAKHAT ? k + 1 : p;
    }

    /** {@code nextStarter[k]}: vị trí đầu tiên từ {@code k} trở đi không phải dấu/nguyên âm đi sau (O(n)). */
    private static int[] nextStarters(String text) {
        int n = text.length();
        int[] nextStarter = new int[n + 1];
        nextStarter[n] = n;
        for (int k = n - 1; k >= 0; k--) {
            nextStarter[k] = isNonStarter(text.charAt(k)) ? nextStarter[k + 1] : k;
        }
        return nextStarter;
    }

    /**
     * Một cụm ký tự: [nguyên âm đứng trước] + ký tự + mọi dấu/nguyên âm không đứng đầu được, tối đa
     * {@value #MAX_CLUSTER_CHARS} ký tự (chuỗi dấu chồng kiểu "zalgo" bị cắt thay vì thành 1 cụm khổng lồ),
     * cộng đuôi câm nếu có (tối đa 4 ký tự).
     */
    private static int clusterEnd(String text, int start, int[] nextStarter) {
        int k = start;
        if (isLeadingVowel(text.charAt(k)) && k + 1 < text.length()) {
            k++;
        }
        k++;
        int end = k < text.length() ? nextStarter[k] : k;
        return karanTailEnd(text, Math.min(end, start + MAX_CLUSTER_CHARS));
    }

    /**
     * Gộp các cụm không có trong từ điển liền nhau (tối đa {@value #MAX_TOKEN_CHARS} ký tự), gắn {@code ๆ} vào token
     * trước. Trả về {start, end, 1 nếu token bắt đầu bằng ký tự dùng chung với token trước}.
     */
    private static List<int[]> mergeUnknown(String text, int[] next, boolean[] known, boolean[] shared) {
        List<int[]> spans = new ArrayList<>();
        int i = 0;
        boolean lastUnknown = false;
        boolean sharedStart = false;
        while (i < text.length()) {
            int end = shared[i] ? next[i] + 1 : next[i];
            boolean fits = !spans.isEmpty() && end - spans.get(spans.size() - 1)[0] <= MAX_TOKEN_CHARS;
            boolean attach = fits && !sharedStart && ((lastUnknown && !known[i]) || text.charAt(i) == MAIYAMOK);
            if (attach) {
                spans.get(spans.size() - 1)[1] = end;
            } else {
                spans.add(new int[]{i, end, sharedStart ? 1 : 0});
            }
            lastUnknown = !known[i] && text.charAt(i) != MAIYAMOK;
            sharedStart = shared[i];
            i = next[i];
        }
        return spans;
    }

    static List<String> readLines(InputStream in) throws IOException {
        List<String> lines = new ArrayList<>();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(in, StandardCharsets.UTF_8))) {
            String line;
            while ((line = reader.readLine()) != null) {
                lines.add(line);
            }
        }
        return lines;
    }

    private static final class Node {
        final Map<Character, Node> children = new HashMap<>(4);
        boolean terminal;
    }
}
