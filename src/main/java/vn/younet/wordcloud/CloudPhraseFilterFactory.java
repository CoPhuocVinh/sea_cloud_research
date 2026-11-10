package vn.younet.wordcloud;

import org.apache.lucene.analysis.CharArraySet;
import org.apache.lucene.analysis.TokenFilterFactory;
import org.apache.lucene.analysis.TokenStream;
import org.apache.lucene.util.ResourceLoader;
import org.apache.lucene.util.ResourceLoaderAware;

import java.io.IOException;
import java.util.Collections;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 * Tham số:
 * <ul>
 *   <li>{@code edgeStopwords}: file stopword chặn ở biên cụm (bắt buộc), vd. {@code lang/cloud_stop_${topic.country:sea}.txt};</li>
 *   <li>{@code tailWords}: file từ được phép đứng cuối cụm dù là stopword (tuỳ chọn);</li>
 *   <li>{@code phrases}: file gazetteer, mỗi dòng 1 cụm viết thường (tuỳ chọn);</li>
 *   <li>{@code vocabulary}: file từ vựng cụm đã đào trước; có thì chỉ giữ cụm trong đó (tuỳ chọn, rỗng = tắt),
 *       vd. {@code vocabulary="${cloud.vocabulary:}"};</li>
 *   <li>{@code minWords}/{@code maxWords}: số từ của cụm, mặc định 2 và 4 (BR-29).</li>
 * </ul>
 */
public class CloudPhraseFilterFactory extends TokenFilterFactory implements ResourceLoaderAware {
    public static final String NAME = "cloudPhrase";

    private final String edgeStopwordsFile;
    private final String tailWordsFile;
    private final String phrasesFile;
    private final String vocabularyFile;
    private final int minWords;
    private final int maxWords;
    private CharArraySet edgeStopwords;
    private CharArraySet tailWords = CharArraySet.EMPTY_SET;
    private Set<String> gazetteer = Collections.emptySet();
    private Set<String> vocabulary = Collections.emptySet();
    private int maxGazetteerTokens;

    public CloudPhraseFilterFactory(Map<String, String> args) {
        super(args);
        edgeStopwordsFile = require(args, "edgeStopwords");
        tailWordsFile = get(args, "tailWords");
        phrasesFile = get(args, "phrases");
        String vocab = get(args, "vocabulary");
        vocabularyFile = vocab == null || vocab.isBlank() ? null : vocab;
        minWords = getInt(args, "minWords", 2);
        maxWords = getInt(args, "maxWords", 4);
        if (!args.isEmpty()) {
            throw new IllegalArgumentException("Unknown parameters: " + args);
        }
    }

    /** Lucene SPI yêu cầu constructor rỗng. */
    public CloudPhraseFilterFactory() {
        throw defaultCtorException();
    }

    @Override
    public void inform(ResourceLoader loader) throws IOException {
        edgeStopwords = getWordSet(loader, edgeStopwordsFile, true);
        if (tailWordsFile != null) {
            tailWords = getWordSet(loader, tailWordsFile, true);
        }
        if (phrasesFile != null) {
            Set<String> phrases = new HashSet<>();
            for (String line : getLines(loader, phrasesFile)) {
                String phrase = CloudPhraseFilter.normalizeEntry(line);
                int tokens = CloudPhraseFilter.countWords(phrase);
                if (tokens >= 2) {
                    phrases.add(phrase);
                    maxGazetteerTokens = Math.max(maxGazetteerTokens, tokens);
                }
            }
            gazetteer = phrases;
        }
        if (vocabularyFile != null) {
            Set<String> vocab = new HashSet<>();
            for (String line : getLines(loader, vocabularyFile)) {
                vocab.add(CloudPhraseFilter.normalizeEntry(line));
            }
            vocabulary = vocab;
        }
    }

    @Override
    public TokenStream create(TokenStream input) {
        return new CloudPhraseFilter(input, gazetteer, maxGazetteerTokens, edgeStopwords, tailWords, vocabulary,
                minWords, maxWords);
    }
}
