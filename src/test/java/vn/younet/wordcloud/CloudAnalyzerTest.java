package vn.younet.wordcloud;

import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.regex.Pattern;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static vn.younet.wordcloud.CloudAnalyzers.phrases;
import static vn.younet.wordcloud.CloudAnalyzers.tokens;

/** Các case lỗi đã ghi trong reports/Case wordcloud 5 nước SEA.md. */
class CloudAnalyzerTest {

    /** Cụm Thái như filter tạo ra: các từ nối bằng U+200B (CloudPhraseFilter.THAI_JOINER). */
    private static String th(String... words) {
        return String.join(String.valueOf(CloudPhraseFilter.THAI_JOINER), words);
    }

    private static String visible(String phrase) {
        return phrase.replace(String.valueOf(CloudPhraseFilter.THAI_JOINER), "");
    }

    @Test
    void thaiToneMarksSurviveNormalization() {
        assertEquals(List.of("ไม่", "ใหม่", "ไหม้", "ไหม", "น้ำ"), tokens("th", "ไม่ ใหม่ ไหม้ ไหม น้ำ"));
    }

    @Test
    void thaiNamesAndBrandsStayWhole() {
        List<String> t = tokens("th", "ยินดีด้วยกับลิซ่า แบล็กพิงก์ สั่งของในช้อปปี้กับลาซาด้า");
        assertTrue(t.containsAll(List.of("ลิซ่า", "แบล็กพิงก์", "ช้อปปี้", "ลาซาด้า")), t.toString());
    }

    @Test
    void thaiElongationAndMaiyamok() {
        assertEquals(List.of("ฟิน", "มาก", "น่ารักๆ"), tokens("th", "ฟินมากกกก 55555 น่ารักๆๆ"));
        assertEquals(List.of("หน้า", "ใส", "ขึ้น", "นี้", "สาย", "แล้ว", "คุณ", "วชิร", "วิชญ์"),
                tokens("th", "หน้าใสขึ้นนนนี้ สายย แล้วว คุณวชิรวิชญ์"));
    }

    @Test
    void thaiSpaceIsPhraseBoundaryAndJoinWithoutSpace() {
        // Stoplist tối thiểu không chặn ถูก ("rẻ") hay มาก: mỗi đoạn giữa 2 dấu cách là 1 vùng riêng,
        // cụm ghép không dấu cách và không vượt sang đoạn khác.
        assertEquals(List.of("ราคา", "ถูก", "มาก"), tokens("th", "ราคาถูกมาก"));
        List<String> p = phrases("th", "ราคาถูกมาก ส่งเร็ว แพ็คดี");
        assertEquals(List.of(th("ราคา", "ถูก"), th("ราคา", "ถูก", "มาก"), th("ถูก", "มาก"), th("ส่ง", "เร็ว"),
                th("แพ็ค", "ดี")), p);
        assertEquals(List.of("ราคาถูก", "ราคาถูกมาก", "ถูกมาก", "ส่งเร็ว", "แพ็คดี"),
                p.stream().map(CloudAnalyzerTest::visible).collect(java.util.stream.Collectors.toList()), "người đọc thấy viết liền");
        assertFalse(p.stream().map(CloudAnalyzerTest::visible)
                .anyMatch(s -> s.contains("มากส่ง") || s.contains("เร็วแพ็ค")), p.toString());
    }

    @Test
    void phrasesNeverCrossSentencePunctuation() {
        List<String> p = phrases("id", "Promo Shopee 10.10 mantap. Harga murah banget! Gratis ongkir lagi");
        assertTrue(p.containsAll(List.of("promo shopee", "harga murah", "gratis ongkir")), p.toString());
        assertTrue(p.contains("shopee 10.10 mantap"), "10.10 không phải ranh giới: " + p);
        assertFalse(p.contains("mantap harga"), p.toString());
        assertFalse(p.contains("banget gratis"), p.toString());
    }

    @Test
    void hashtagsUrlsAndMentionsAreRemoved() {
        List<String> p = phrases("id", "#IndonesianIdol Raisa keren cek https://shope.ee/abc123 @shopee_id sekarang wkwkwk 😂 lucu sekali");
        assertTrue(p.contains("raisa keren"), p.toString());
        assertFalse(p.stream().anyMatch(s -> s.contains("indonesianidol") || s.contains("shope") || s.contains("wkwk")), p.toString());
    }

    @Test
    void gazetteerKeepsNamesWholeRegardlessOfCase() {
        List<String> p = phrases("ms", "Tahniah Dato' Sri Siti Nurhaliza atas Anugerah Juara Lagu ke-40!");
        assertTrue(p.containsAll(List.of("siti nurhaliza", "anugerah juara lagu")), p.toString());
        // Gazetteer là 1 khối: không cắt "nurhaliza" ra ghép với từ sau; "atas" là giới từ nên không kết cụm.
        // Kính ngữ (dato, sri) không phải từ nối nên được giữ — bước làm sạch/gazetteer quyết định hiển thị.
        assertFalse(p.stream().anyMatch(s -> s.endsWith(" atas") || s.startsWith("nurhaliza")), p.toString());
        assertTrue(phrases("id", "selamat untuk RAISA ANDRIANA dan hamish daud").containsAll(List.of("raisa andriana", "hamish daud")));
    }

    @Test
    void digitReduplicationAndElongation() {
        List<String> p = phrases("id", "Anak-anak suka jalan2 ke mall, suaranya merdu bangetttt");
        assertTrue(p.contains("jalan jalan"), p.toString());
        assertFalse(p.stream().anyMatch(s -> s.contains("ttt") || s.contains("jalan2")), p.toString());
    }

    /** Hồi quy: token láy đứng sau ranh giới từng làm offset của cụm bị ngược (data VN thật, "h T,VL2"). */
    @Test
    void reduplicationAfterBoundaryKeepsValidOffsets() {
        assertEquals(List.of("h t", "vl vl"), phrases("vi", "h T,VL2"));
        assertTrue(phrases("id", "suka, jalan2 terus").contains("jalan jalan"));
    }

    @Test
    void slangMapsToCanonicalForm() {
        assertTrue(tokens("id", "gak sabar nggak sabar").stream().filter("tidak"::equals).count() == 2);
        assertTrue(tokens("tl", "sobrang saya lng tlga").containsAll(List.of("lang", "talaga")));
    }

    @Test
    void minimalStoplistHasNoCrossLanguageCollision() {
        // "saya" = "tôi" (id/ms) nhưng = "vui" (tl). Bộ dự phòng "sea" (không biết nước) chỉ gồm từ nối nên không
        // chặn nhầm; đại từ chỉ có trong stoplist của đúng nước (stoplist lớn cũ từng chặn "sobrang saya").
        assertTrue(phrases("tl", "Grabe sobrang saya naman").contains("sobrang saya"));
        assertTrue(phrases("sea", "Grabe sobrang saya naman").contains("sobrang saya"));
    }

    @Test
    void singaporeanPossessiveAndChineseMix() {
        assertTrue(phrases("sg", "Singapore's NDP 2026 was amazing").contains("singapore ndp"));
        List<String> p = phrases("sg", "Hawker centre 的 char kway teow 很好吃 leh");
        assertTrue(p.containsAll(List.of("hawker centre", "char kway teow")), p.toString());
    }

    @Test
    void hashtagsAreExtractedLowercaseNfc() {
        assertEquals(List.of("#tinhhasayhi", "#raisaandriana", "#hamishdaud", "#ลิซ่า"),
                List.copyOf(CloudFieldsUpdateProcessorFactory.extractHashtags("#TinhHaSayHi #RaisaAndriana#HamishDaud #ลิซ่า")));
    }

    /** Hồi quy review: dấu nháy cong (iOS) phải khớp stoplist như dấu nháy thẳng. */
    @Test
    void curlyApostropheMatchesStopwords() {
        assertEquals(phrases("sg", "I don't know lah"), phrases("sg", "I don’t know lah"));
    }

    /** Hồi quy review: kéo dài giữa từ còn 2 chữ, cuối từ còn 1. */
    @Test
    void elongationKeepsEnglishDoubleLetters() {
        assertTrue(phrases("sg", "goooood food sooo cooool").containsAll(List.of("good food", "food so cool")),
                phrases("sg", "goooood food sooo cooool").toString());
        assertEquals(List.of("banget"), tokens("id", "bangetttt"));
    }

    /** Hồi quy review: part2/season2 không phải láy. */
    @Test
    void digitSuffixIsNotAlwaysReduplication() {
        assertEquals(List.of("season2", "part2"), tokens("sg", "season2 part2"));
    }

    /** Hồi quy review: NBSP giữa hai chữ Thái cũng là ranh giới. */
    @Test
    void nbspBetweenThaiIsBoundary() {
        for (String span : CloudAnalyzers.coveredSpans("th", "อร่อยมาก\u00A0ราคาดี")) {
            assertFalse(span.contains("\u00A0"), span);
        }
    }

    @Test
    void hashtagsIgnoreUrlFragmentsEntitiesAndNumbers() {
        assertEquals(List.of("#ok2"), List.copyOf(CloudFieldsUpdateProcessorFactory.extractHashtags(
                "see https://x.com/page#section it&#39;s #ok2 #123")));
    }

    @Test
    void vocabularyKeepsOnlyKnownPhrasesPlusGazetteer() throws java.io.IOException {
        org.apache.lucene.analysis.Analyzer a = org.apache.lucene.analysis.custom.CustomAnalyzer.builder(CloudAnalyzers.CONF)
                .withTokenizer(ScriptRoutingTokenizerFactory.class)
                .addTokenFilter("icuNormalizer2", "form", "nfkc_cf")
                .addTokenFilter(CloudPhraseFilterFactory.class, "edgeStopwords", "lang/cloud_stop_ms.txt",
                        "phrases", "dict/cloud_names_ms.txt", "vocabulary", "dict/test_vocabulary.txt")
                .build();
        List<String> out = new java.util.ArrayList<>();
        try (org.apache.lucene.analysis.TokenStream ts = a.tokenStream("f", "Tahniah Siti Nurhaliza atas Anugerah Juara Lagu. Juara lagu baru")) {
            org.apache.lucene.analysis.tokenattributes.CharTermAttribute t =
                    ts.addAttribute(org.apache.lucene.analysis.tokenattributes.CharTermAttribute.class);
            ts.reset();
            while (ts.incrementToken()) {
                out.add(t.toString());
            }
            ts.end();
        }
        assertEquals(List.of("siti nurhaliza", "anugerah juara lagu", "juara lagu"), out);
    }

    /** Gazetteer Thái: dòng "ลิซ่า แบล็กพิงก์" khớp cụm viết liền và là 1 khối không bị cắt. */
    @Test
    void thaiGazetteerMatchesWithInvisibleJoiner() {
        List<String> p = phrases("th", "ยินดีด้วยกับลิซ่าแบล็กพิงก์");
        assertTrue(p.contains(th("ลิซ่า", "แบล็กพิงก์")), p.toString());
        assertFalse(p.stream().anyMatch(s -> s.endsWith(th("กับ", "ลิซ่า"))), p.toString());
    }

    /** Hồi quy data tổng hợp: phủ định không bị chặn, từ nhấn mạnh được đứng cuối, stoplist ms không còn từ nội dung. */
    @Test
    void negationAndIntensifierPhrasesSurvive() {
        assertTrue(phrases("id", "gak sabar, keren banget").containsAll(List.of("tidak sabar", "keren banget")),
                phrases("id", "gak sabar, keren banget").toString());
        assertTrue(phrases("tl", "sulit talaga, grabe naman").containsAll(List.of("sulit talaga", "grabe naman")));
        assertTrue(phrases("ms", "harga minyak naik, rakyat marah").containsAll(List.of("harga minyak", "rakyat marah")));
        assertTrue(phrases("th", "ส่งไว เพลงเพราะ").containsAll(List.of(th("ส่ง", "ไว"), th("เพลง", "เพราะ"))),
                phrases("th", "ส่งไว เพลงเพราะ").toString());
        assertTrue(phrases("sg", "must try").contains("must try"));
    }

    /** Bản dùng thật (copyField + TextField): hashtag nằm cùng trường, giữ "#", là ranh giới cụm. */
    @Test
    void hashtagsAreEmittedAsTokensWhenEnabled() {
        List<String> p = CloudAnalyzers.phrasesWithHashtags("id",
                "Keren banget #IndonesianIdol konser raisa https://x.com/a#frag #Raisa#Hamish");
        assertTrue(p.containsAll(List.of("#indonesianidol", "#raisa", "#hamish", "keren banget", "konser raisa")), p.toString());
        assertFalse(p.stream().anyMatch(s -> s.contains("frag") || s.contains("banget #") || s.contains("indonesianidol konser")),
                p.toString());
        assertFalse(phrases("id", "Keren banget #IndonesianIdol").contains("#indonesianidol"), "mặc định tắt");
    }

    /** Hồi quy: hashtag giữa văn bản từng làm offset lùi -> IndexWriter từ chối cả tài liệu (copyField + TextField). */
    @Test
    void offsetsNeverGoBackwardsWithHashtags() throws IOException {
        List<String> texts = new java.util.ArrayList<>(List.of(
                "Uji atomic update kopi susu gula aren #KopiTest lanjut kopi susu", "#a #b kopi susu gula #c kopi"));
        for (String line : Files.readAllLines(Path.of("src/test/resources/cases.tsv"), StandardCharsets.UTF_8)) {
            texts.add(line.split("\t")[2]);
        }
        for (String text : texts) {
            List<Integer> starts = CloudAnalyzers.startOffsetsWithHashtags("id", text);
            for (int i = 1; i < starts.size(); i++) {
                assertTrue(starts.get(i) >= starts.get(i - 1), text + " -> " + starts);
            }
        }
    }

    /** Thuộc tính chung trên 49 case: không cụm nào phủ qua dấu kết câu (BR-29). */
    @Test
    void allCasesRespectSentenceBoundaries() throws IOException {
        Pattern boundary = Pattern.compile("[!?;\\n…]|[.,:](?!\\d)");
        for (String line : Files.readAllLines(Path.of("src/test/resources/cases.tsv"), StandardCharsets.UTF_8)) {
            String[] f = line.split("\t");
            String country = f[0];
            for (String span : CloudAnalyzers.coveredSpans(country, f[2])) {
                assertFalse(boundary.matcher(span).find(), f[0] + "/" + f[1] + " crosses boundary: " + span);
            }
        }
    }
}
