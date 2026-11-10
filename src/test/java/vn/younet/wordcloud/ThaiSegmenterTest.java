package vn.younet.wordcloud;

import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class ThaiSegmenterTest {

    private static List<String> segment(ThaiSegmenter s, String text) {
        List<String> out = new ArrayList<>();
        for (int[] span : s.segment(text)) {
            out.add(text.substring(span[0], span[1]));
        }
        return out;
    }

    @Test
    void neverSplitsInsideACharacterCluster() throws IOException {
        // Không có trong từ điển: vẫn không được cắt kiểu ICU (ซาด้|า, ล็ก|ก์)
        for (String token : segment(ThaiSegmenter.withDefaultDictionary(), "ลาซาด้าแบล็กพิงก์ติ๊กต็อก")) {
            assertFalse(ThaiSegmenter.isNonStarter(token.charAt(0)), token);
        }
    }

    @Test
    void userDictionaryWins() throws IOException {
        ThaiSegmenter s = ThaiSegmenter.withDefaultDictionary().addAll(List.of("ลาซาด้า", "ช้อปปี้"));
        assertEquals(List.of("สั่ง", "ของ", "ใน", "ช้อปปี้", "กับ", "ลาซาด้า"), segment(s, "สั่งของในช้อปปี้กับลาซาด้า"));
    }

    /** Hồi quy review: chuỗi dấu chồng ("zalgo") từng chạy O(n²) và sinh token > 32766 byte. */
    @Test
    void stackedMarksAreLinearAndBounded() throws IOException {
        ThaiSegmenter s = ThaiSegmenter.withDefaultDictionary();
        String zalgo = "ก" + "\u0E49\u0E34".repeat(20_000);
        long start = System.nanoTime();
        List<int[]> spans = s.segment(zalgo);
        assertTrue(System.nanoTime() - start < 1_000_000_000L, "segment quá chậm");
        for (int[] span : spans) {
            assertTrue(span[1] - span[0] <= ThaiSegmenter.MAX_TOKEN_CHARS);
        }
    }

    @Test
    void consecutiveUnknownClustersMergeIntoOneToken() throws IOException {
        ThaiSegmenter s = ThaiSegmenter.withDefaultDictionary();
        assertEquals(List.of("กิน", "ฮฺฮฺฮฺ"), segment(s, "กินฮฺฮฺฮฺ"));
    }

    /** Hồi quy compare_thai_seg: đuôi câm (ต์, ชญ์) từng bị tách thành token riêng. */
    @Test
    void silentTailStaysWithPreviousCluster() throws IOException {
        ThaiSegmenter s = ThaiSegmenter.withDefaultDictionary();
        assertEquals(List.of("สงกา", "รนต์"), segment(s, "สงการนต์"));
        assertEquals(List.of("คุณ", "วชิร", "วิชญ์"), segment(s, "คุณวชิรวิชญ์"));
        assertEquals(List.of("ซื้อ", "การ์ด", "วัน", "จันทร์"), segment(s, "ซื้อการ์ดวันจันทร์"));
    }

    private static List<String> tokenize(ThaiSegmenter s, String text) {
        List<String> out = new ArrayList<>();
        for (ThaiSegmenter.Word w : s.tokenize(text)) {
            out.add(w.term + "@" + w.start + "-" + w.end);
        }
        return out;
    }

    /** Hồi quy compare_thai_seg: kéo dài 2 ký tự (สายย, แล้วว, เยอะะ) từng sinh token 1 ký tự. */
    @Test
    void twoCharElongationJoinsPreviousWord() throws IOException {
        ThaiSegmenter s = ThaiSegmenter.withDefaultDictionary();
        assertEquals(List.of("สาย@0-4"), tokenize(s, "สายย"));
        assertEquals(List.of("แล้ว@0-5"), tokenize(s, "แล้วว"));
        assertEquals(List.of("เยอะ@0-5"), tokenize(s, "เยอะะ"));
        assertEquals(List.of("มาก@0-6"), tokenize(s, "มากกกก"));
        assertEquals(List.of("ไป@0-2", "นนทบุรี@2-9"), tokenize(s, "ไปนนทบุรี"), "phụ âm đôi thật không bị gộp");
    }

    /** Hồi quy compare_thai_seg: ขึ้นนนนี้ từng bị rút mất chữ đầu của นี้ (ขึ้|นนนนี้). */
    @Test
    void elongatedLetterCanStartTheNextWord() throws IOException {
        ThaiSegmenter s = ThaiSegmenter.withDefaultDictionary();
        assertEquals(List.of("ขึ้น@0-6", "นี้@6-9"), tokenize(s, "ขึ้นนนนี้"));
        assertEquals(List.of("ฟิน@0-3", "มาก@3-9"), tokenize(s, "ฟินมากกกก"), "không thành มา|กก");
        assertEquals(List.of("มาก@0-4", "กว่า@4-8"), tokenize(s, "มากกกว่า"), "hoà điểm với มา|กว่า");
        assertEquals(List.of("นาน@0-5", "นะ@5-7"), tokenize(s, "นานนนนะ"), "hoà điểm với นา|นะ");
    }

    @Test
    void thaiDigitsAreNotCollapsed() throws IOException {
        assertEquals("๒๐๐๐", ThaiSegmenter.withDefaultDictionary().tokenize("๒๐๐๐").get(0).term);
    }
}
