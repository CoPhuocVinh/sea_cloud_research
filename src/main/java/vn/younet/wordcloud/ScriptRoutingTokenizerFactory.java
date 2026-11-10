package vn.younet.wordcloud;

import org.apache.lucene.analysis.TokenizerFactory;
import org.apache.lucene.util.AttributeFactory;
import org.apache.lucene.util.ResourceLoader;
import org.apache.lucene.util.ResourceLoaderAware;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Tham số {@code thaiDict} (tuỳ chọn): file trong configset, mỗi dòng 1 từ Thái bổ sung cho từ điển
 * mặc định (thương hiệu, tên người, slang), vd. {@code thaiDict="dict/thai_extra.txt"}.
 * {@code emitHashtags} (mặc định false): phát hashtag thành token (xem {@link ScriptRoutingTokenizer}).
 */
public class ScriptRoutingTokenizerFactory extends TokenizerFactory implements ResourceLoaderAware {
    public static final String NAME = "scriptRouting";
    /** Trie Thái (~30 MB) chỉ đọc sau khi dựng: các core cùng từ điển bổ sung dùng chung 1 bản. */
    private static final Map<List<String>, ThaiSegmenter> SEGMENTERS = new ConcurrentHashMap<>();

    private final String thaiDict;
    private final boolean emitHashtags;
    private ThaiSegmenter segmenter;

    public ScriptRoutingTokenizerFactory(Map<String, String> args) {
        super(args);
        thaiDict = get(args, "thaiDict");
        emitHashtags = getBoolean(args, "emitHashtags", false);
        if (!args.isEmpty()) {
            throw new IllegalArgumentException("Unknown parameters: " + args);
        }
    }

    /** Lucene SPI yêu cầu constructor rỗng. */
    public ScriptRoutingTokenizerFactory() {
        throw defaultCtorException();
    }

    @Override
    public void inform(ResourceLoader loader) throws IOException {
        List<String> extra = thaiDict == null ? List.of() : List.copyOf(getLines(loader, thaiDict));
        segmenter = SEGMENTERS.computeIfAbsent(extra, words -> {
            try {
                return ThaiSegmenter.withDefaultDictionary().addAll(words);
            } catch (IOException e) {
                throw new UncheckedIOException(e);
            }
        });
    }

    @Override
    public ScriptRoutingTokenizer create(AttributeFactory factory) {
        return new ScriptRoutingTokenizer(factory, segmenter, emitHashtags);
    }
}
