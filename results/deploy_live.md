# Facet search_text_cloud (copyField + TextField) khi mention đổ vào liên tục

Sinh bởi `scripts/deploy_measure_vn.sh` (Solr 9.10.1 Docker, heap 4 GB, cổng 8986). Data: 2 file export VN
(458 232 mention gửi → ~328 700 sau SkipExistingDocuments của topic_global). Mỗi core đo 90 giây: luồng ghi gửi 50
mention mới mỗi 2 giây (không commit, để autoSoftCommit 5 s của topic_global mở searcher mới), luồng đọc gửi 1 truy vấn
facet top 100 mỗi giây. Độ tươi = thời gian từ lúc gửi tới lúc mention tìm thấy được.

| Core | Cụm khác nhau | Index | Số truy vấn trong 90 s | Facet p50 | Facet p95 | Facet max | Độ tươi p50 / max |
|---|---|---|---|---|---|---|---|
| mọi n-gram, không warming | ~5,6 triệu | 1 016 MB | 5 | 19,9 s | 25,7 s | 25,7 s | 3,2 / 5,7 s |
| mọi n-gram, có warming | ~5,6 triệu | 998 MB | 39 | 66 ms | **18,9 s** | 25,3 s | 13,1 / 36,0 s |
| **pha 2 (từ vựng 132 752 cụm), có warming** | ≤ 132 752 | 663 MB | 58 | **18 ms** | **3,6 s** | 4,0 s | 3,7 / 5,8 s |

- Không pha 2: un-invert ~20 s mỗi searcher mới, lâu hơn chu kỳ soft commit 5 s → không dùng được. Warming chỉ đổi
  độ trễ lấy độ tươi (mention mới hiện sau tới 36 s) mà p95 vẫn 19 s.
- Có pha 2: p95 3,6 s, max 4,0 s — dưới mục tiêu 5 s nhưng sát; mention mới hiện sau ~4–6 s.
- Từ vựng đào in-sample từ chính core (min-count 20); bản thật cần job đào theo topic + chỗ lưu file ngoài ZooKeeper.
