package vn.younet.wordcloud;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.TokenStream;
import org.apache.lucene.analysis.custom.CustomAnalyzer;
import org.apache.lucene.analysis.tokenattributes.CharTermAttribute;
import org.apache.lucene.analysis.tokenattributes.OffsetAttribute;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Dựng lại đúng chain {@code text_cloud_sea} của schema.xml, đọc tài nguyên từ chính configset
 * (một nguồn duy nhất), với {@code ${topic.country}} thay bằng tham số {@code country}.
 */
final class CloudAnalyzers {
    static final Path CONF = Path.of("docker/configsets/sea_cloud/conf");
    private static final Map<String, Analyzer> PHRASE = new HashMap<>();
    private static final Map<String, Analyzer> TOKEN = new HashMap<>();

    private CloudAnalyzers() {
    }

    private static final Map<String, Analyzer> WITH_HASHTAGS = new HashMap<>();

    /** Cụm wordcloud mà analyzer phát ra. */
    static List<String> phrases(String country, String text) {
        return terms(PHRASE.computeIfAbsent(country, c -> build(c, true, false)), text);
    }

    /** Như bản dùng thật trong schema: tokenizer emitHashtags="true". */
    static List<String> phrasesWithHashtags(String country, String text) {
        return terms(WITH_HASHTAGS.computeIfAbsent(country, c -> build(c, true, true)), text);
    }

    /** Token trước bước ghép cụm (để kiểm tách từ / chuẩn hoá). */
    static List<String> tokens(String country, String text) {
        return terms(TOKEN.computeIfAbsent(country, c -> build(c, false, false)), text);
    }

    /** Start offset của từng token (bản có hashtag) — IndexWriter từ chối nếu offset lùi. */
    static List<Integer> startOffsetsWithHashtags(String country, String text) {
        List<Integer> out = new ArrayList<>();
        Analyzer analyzer = WITH_HASHTAGS.computeIfAbsent(country, c -> build(c, true, true));
        try (TokenStream ts = analyzer.tokenStream("f", text)) {
            OffsetAttribute off = ts.addAttribute(OffsetAttribute.class);
            ts.reset();
            while (ts.incrementToken()) {
                out.add(off.startOffset());
            }
            ts.end();
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
        return out;
    }

    /** Cụm kèm đoạn văn bản gốc mà nó phủ (để kiểm không vượt ranh giới câu). */
    static List<String> coveredSpans(String country, String text) {
        List<String> spans = new ArrayList<>();
        Analyzer analyzer = PHRASE.computeIfAbsent(country, c -> build(c, true, false));
        try (TokenStream ts = analyzer.tokenStream("f", text)) {
            OffsetAttribute off = ts.addAttribute(OffsetAttribute.class);
            ts.reset();
            while (ts.incrementToken()) {
                spans.add(text.substring(off.startOffset(), off.endOffset()));
            }
            ts.end();
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
        return spans;
    }

    private static List<String> terms(Analyzer analyzer, String text) {
        List<String> out = new ArrayList<>();
        try (TokenStream ts = analyzer.tokenStream("f", text)) {
            CharTermAttribute term = ts.addAttribute(CharTermAttribute.class);
            ts.reset();
            while (ts.incrementToken()) {
                out.add(term.toString());
            }
            ts.end();
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
        return out;
    }

    private static Analyzer build(String country, boolean withPhrases, boolean hashtags) {
        try {
            CustomAnalyzer.Builder b = CustomAnalyzer.builder(CONF)
                    .withTokenizer(ScriptRoutingTokenizerFactory.class, "thaiDict", "dict/thai_extra.txt",
                            "emitHashtags", String.valueOf(hashtags))
                    .addTokenFilter("icuNormalizer2", "form", "nfkc_cf", "mode", "compose", "filter", "[^[:Thai:]]")
                    .addTokenFilter(SocialNormalizeFilterFactory.class, "slang", "lang/cloud_slang_" + country + ".txt");
            if (withPhrases) {
                b.addTokenFilter(CloudPhraseFilterFactory.class,
                        "edgeStopwords", "lang/cloud_stop_" + country + ".txt",
                        "tailWords", "lang/cloud_tail_" + country + ".txt",
                        "phrases", "dict/cloud_names_" + country + ".txt");
            }
            return b.build();
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }
}
