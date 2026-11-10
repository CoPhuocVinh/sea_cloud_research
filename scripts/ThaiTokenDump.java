import org.apache.lucene.analysis.Tokenizer;
import org.apache.lucene.analysis.icu.segmentation.ICUTokenizer;
import org.apache.lucene.analysis.th.ThaiTokenizer;
import org.apache.lucene.analysis.tokenattributes.OffsetAttribute;
import org.apache.lucene.util.AttributeFactory;
import vn.younet.wordcloud.ScriptRoutingTokenizer;
import vn.younet.wordcloud.ThaiSegmenter;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.StringReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Supplier;

/**
 * Tách từ mỗi dòng của file đầu vào bằng các tokenizer Java, cho scripts/compare_thai_seg.py.
 *
 *     java -cp target/classes:<deps> scripts/ThaiTokenDump.java <in.txt> <out.tsv> <thai_extra.txt>
 *
 * Đầu ra: mỗi dòng "engine \t số dòng \t start:end,start:end,..." (offset UTF-16 trên văn bản gốc),
 * cuối file thêm dòng "#time \t engine \t ms".
 * - sea        : ScriptRoutingTokenizer (ThaiSegmenter + từ điển thai_extra như configset, ICU cho phần còn lại)
 * - lucene_th  : org.apache.lucene.analysis.th.ThaiTokenizer (BreakIterator của JDK)
 * - icu        : ICUTokenizer (từ điển Thái của ICU4J)
 */
public class ThaiTokenDump {
    public static void main(String[] args) throws IOException {
        List<String> lines = Files.readAllLines(Path.of(args[0]), StandardCharsets.UTF_8);
        ThaiSegmenter segmenter = ThaiSegmenter.withDefaultDictionary().addAll(extraWords(Path.of(args[2])));
        Map<String, Supplier<Tokenizer>> engines = new LinkedHashMap<>();
        engines.put("sea", () -> new ScriptRoutingTokenizer(AttributeFactory.DEFAULT_ATTRIBUTE_FACTORY, segmenter, false));
        engines.put("lucene_th", ThaiTokenizer::new);
        engines.put("icu", ICUTokenizer::new);
        try (BufferedWriter out = Files.newBufferedWriter(Path.of(args[1]), StandardCharsets.UTF_8)) {
            for (Map.Entry<String, Supplier<Tokenizer>> e : engines.entrySet()) {
                long t0 = System.nanoTime();
                List<String> rows = spans(e.getValue().get(), lines);
                long ms = (System.nanoTime() - t0) / 1_000_000;
                for (int i = 0; i < rows.size(); i++) {
                    out.write(e.getKey() + "\t" + i + "\t" + rows.get(i) + "\n");
                }
                out.write("#time\t" + e.getKey() + "\t" + ms + "\n");
            }
        }
    }

    private static List<String> extraWords(Path path) throws IOException {
        List<String> words = new ArrayList<>();
        try (BufferedReader r = Files.newBufferedReader(path, StandardCharsets.UTF_8)) {
            for (String line; (line = r.readLine()) != null; ) {
                line = line.strip();
                if (!line.isEmpty() && !line.startsWith("#")) {
                    words.add(line);
                }
            }
        }
        return words;
    }

    private static List<String> spans(Tokenizer tokenizer, List<String> lines) throws IOException {
        OffsetAttribute offset = tokenizer.addAttribute(OffsetAttribute.class);
        List<String> rows = new ArrayList<>(lines.size());
        for (String line : lines) {
            StringBuilder sb = new StringBuilder();
            tokenizer.setReader(new StringReader(line));
            tokenizer.reset();
            while (tokenizer.incrementToken()) {
                if (sb.length() > 0) {
                    sb.append(',');
                }
                sb.append(offset.startOffset()).append(':').append(offset.endOffset());
            }
            tokenizer.end();
            tokenizer.close();
            rows.add(sb.toString());
        }
        return rows;
    }
}
