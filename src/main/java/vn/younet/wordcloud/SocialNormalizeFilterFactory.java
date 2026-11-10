package vn.younet.wordcloud;

import org.apache.lucene.analysis.TokenFilterFactory;
import org.apache.lucene.analysis.TokenStream;
import org.apache.lucene.util.ResourceLoader;
import org.apache.lucene.util.ResourceLoaderAware;

import java.io.IOException;
import java.util.Collections;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;

/**
 * Tham số {@code slang} (tuỳ chọn): file ánh xạ, mỗi dòng {@code a,b => chuẩn} (chỉ 1 từ -&gt; 1 từ),
 * vd. {@code slang="lang/cloud_slang_${topic.country:sea}.txt"}.
 */
public class SocialNormalizeFilterFactory extends TokenFilterFactory implements ResourceLoaderAware {
    public static final String NAME = "socialNormalize";

    private final String slangFile;
    private Map<String, String> slang = Collections.emptyMap();

    public SocialNormalizeFilterFactory(Map<String, String> args) {
        super(args);
        slangFile = get(args, "slang");
        if (!args.isEmpty()) {
            throw new IllegalArgumentException("Unknown parameters: " + args);
        }
    }

    /** Lucene SPI yêu cầu constructor rỗng. */
    public SocialNormalizeFilterFactory() {
        throw defaultCtorException();
    }

    @Override
    public void inform(ResourceLoader loader) throws IOException {
        if (slangFile != null) {
            slang = parseSlang(getLines(loader, slangFile));
        }
    }

    static Map<String, String> parseSlang(Iterable<String> lines) {
        Map<String, String> map = new HashMap<>();
        for (String line : lines) {
            String[] parts = line.split("=>");
            if (parts.length != 2) {
                throw new IllegalArgumentException("Expected 'a,b => c': " + line);
            }
            String target = parts[1].trim().toLowerCase(Locale.ROOT);
            for (String source : parts[0].split(",")) {
                map.put(source.trim().toLowerCase(Locale.ROOT), target);
            }
        }
        return map;
    }

    @Override
    public TokenStream create(TokenStream input) {
        return new SocialNormalizeFilter(input, slang);
    }
}
