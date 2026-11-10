package vn.younet.wordcloud;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.TokenStream;
import org.apache.lucene.analysis.tokenattributes.CharTermAttribute;
import org.apache.solr.common.SolrException;
import org.apache.solr.common.SolrInputDocument;
import org.apache.solr.common.util.NamedList;
import org.apache.solr.request.SolrQueryRequest;
import org.apache.solr.response.SolrQueryResponse;
import org.apache.solr.schema.FieldType;
import org.apache.solr.update.AddUpdateCommand;
import org.apache.solr.update.processor.UpdateRequestProcessor;
import org.apache.solr.update.processor.UpdateRequestProcessorFactory;

import java.io.IOException;
import java.text.Normalizer;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import java.util.LinkedHashSet;
import java.util.Locale;
import java.util.Set;

/**
 * Tính sẵn cụm và hashtag lúc index, ghi vào 2 trường StrField multiValued có docValues để facet nhanh.
 *
 * <pre>
 * &lt;processor class="vn.younet.wordcloud.CloudFieldsUpdateProcessorFactory"&gt;
 *   &lt;str name="sourceField"&gt;search_text&lt;/str&gt;
 *   &lt;int name="sourceIndex"&gt;1&lt;/int&gt;          &lt;!-- BR-27: chỉ phần tử số 2 --&gt;
 *   &lt;str name="analyzerFieldType"&gt;text_cloud_sea&lt;/str&gt;
 *   &lt;str name="phrasesField"&gt;cloud_phrases&lt;/str&gt;
 *   &lt;str name="hashtagsField"&gt;cloud_hashtags&lt;/str&gt;
 * &lt;/processor&gt;
 * </pre>
 * Mọi token analyzer phát ra đều được lấy làm cụm, nên analyzer phải tự lọc (vd. kết thúc bằng
 * {@link CloudPhraseFilter}). Đặt processor <b>sau</b> {@code DistributedUpdateProcessorFactory}: tới đó atomic
 * update ({@code {"set": ...}}) đã được gộp thành tài liệu đầy đủ. Tài liệu không có trường nguồn được bỏ qua.
 */
public class CloudFieldsUpdateProcessorFactory extends UpdateRequestProcessorFactory {
    private String sourceField;
    private int sourceIndex;
    private String analyzerFieldType;
    private String phrasesField;
    private String hashtagsField;

    @Override
    public void init(NamedList<?> args) {
        sourceField = required(args, "sourceField");
        Object index = args.get("sourceIndex");
        sourceIndex = index == null ? 0 : Integer.parseInt(index.toString());
        analyzerFieldType = required(args, "analyzerFieldType");
        phrasesField = required(args, "phrasesField");
        hashtagsField = required(args, "hashtagsField");
    }

    private static String required(NamedList<?> args, String name) {
        Object value = args.get(name);
        if (value == null) {
            throw new SolrException(SolrException.ErrorCode.SERVER_ERROR, "Missing parameter: " + name);
        }
        return value.toString();
    }

    @Override
    public UpdateRequestProcessor getInstance(SolrQueryRequest req, SolrQueryResponse rsp, UpdateRequestProcessor next) {
        FieldType type = req.getSchema().getFieldTypeByName(analyzerFieldType);
        if (type == null) {
            throw new SolrException(SolrException.ErrorCode.SERVER_ERROR, "Unknown fieldType: " + analyzerFieldType);
        }
        return new Processor(type.getIndexAnalyzer(), next);
    }

    private final class Processor extends UpdateRequestProcessor {
        private final Analyzer analyzer;

        Processor(Analyzer analyzer, UpdateRequestProcessor next) {
            super(next);
            this.analyzer = analyzer;
        }

        @Override
        public void processAdd(AddUpdateCommand cmd) throws IOException {
            SolrInputDocument doc = cmd.getSolrInputDocument();
            String text = pickSource(doc.getFieldValues(sourceField));
            if (text != null) {
                doc.setField(hashtagsField, new ArrayList<>(extractHashtags(text)));
                doc.setField(phrasesField, new ArrayList<>(analyze(text)));
            }
            super.processAdd(cmd);
        }

        private String pickSource(Collection<Object> values) {
            if (values == null || values.size() <= sourceIndex) {
                return null;
            }
            Iterator<Object> it = values.iterator();
            for (int i = 0; i < sourceIndex; i++) {
                it.next();
            }
            Object value = it.next();
            if (value instanceof java.util.Map) {
                throw new SolrException(SolrException.ErrorCode.SERVER_ERROR,
                        "Atomic update chưa được gộp: đặt processor sau DistributedUpdateProcessorFactory");
            }
            return value == null ? null : value.toString();
        }

        private Set<String> analyze(String text) throws IOException {
            Set<String> phrases = new LinkedHashSet<>();
            try (TokenStream ts = analyzer.tokenStream(phrasesField, text)) {
                CharTermAttribute term = ts.addAttribute(CharTermAttribute.class);
                ts.reset();
                while (ts.incrementToken()) {
                    phrases.add(term.toString());
                }
                ts.end();
            }
            return phrases;
        }
    }

    /** BR-31: hashtag viết thường, chuẩn NFC, giữ dấu. Bỏ phần {@code #fragment} nằm trong URL. */
    static Set<String> extractHashtags(String text) {
        Set<String> tags = new LinkedHashSet<>();
        for (int[] span : CloudPatterns.hashtagSpans(text)) {
            String tag = text.substring(span[0], span[1]);
            tags.add(Normalizer.normalize(tag, Normalizer.Form.NFC).toLowerCase(Locale.ROOT));
        }
        return tags;
    }
}
