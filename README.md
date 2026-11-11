# sea_cloud_research

Plugin Solr 9.10 sinh **cụm wordcloud 2–4 từ + hashtag** cho topic_global (Indonesia, Malaysia, Thái Lan,
Philippines, Singapore) bằng **một analyzer duy nhất**; chỉ file tài nguyên khác nhau theo nước. Có môi trường
Docker để so với `vncore_nlp_research` / `solr_facet_research` trên data VN thật.

## Kiến trúc

```
search_text (mọi phần tử) ──copyField──► search_text_cloud  (TextField, type text_cloud_sea)  BR-26
  analyzer text_cloud_sea:
    ScriptRoutingTokenizer   Thái → ThaiSegmenter (maximal matching, words_th CC0 + dict/thai_extra.txt)
                             còn lại → ICUTokenizer (Latin, Hán, emoji); bỏ URL, @mention
                             hashtag → 1 token "#…" (emitHashtags="true")                          BR-31
                             ranh giới câu / dấu cách giữa chữ Thái / hashtag / URL / @ → posInc 2  BR-29
    ICUNormalizer2 nfkc_cf   filter="[^[:Thai:]]" (không phá dấu thanh Thái)
    SocialNormalizeFilter    emoji, tiếng cười, kéo dài, jalan2, 's, slang
    CloudPhraseFilter        gazetteer khớp dài nhất + n-gram 2–4, từ nối không đứng ở biên        BR-30
                             pha 2: chỉ giữ cụm có trong từ vựng ${cloud.vocabulary}
  → term = cụm 2–4 từ + hashtag

wordcloud: json.facet terms trên search_text_cloud (listener warming un-invert sau mỗi commit)
lọc theo cụm: fq={!term f=search_text_cloud}<cụm>
```

Thiết kế cũ (trước 23/10/2026): `CloudFieldsUpdateProcessor` tính cụm/hashtag lúc index vào trường StrField docValues
`cloud_phrases`/`cloud_hashtags` (giữ được BR-27). Nay chỉ còn trong configset thí nghiệm `docker/`; lý do đổi xem
mục "Chuyển hẳn sang copyField + TextField" bên dưới.

Tài nguyên theo nước: `lang/cloud_stop_${topic.country:sea}.txt`, `lang/cloud_slang_*.txt`,
`dict/cloud_names_*.txt`. `topic.country` là core property (đặt lúc tạo collection: `property.topic.country=th`);
thiếu thì dùng bộ gộp `sea`. Stopword sinh bằng `scripts/build_resources.py` từ `resources_src/`
(Lucene Apache-2.0, stopwords-iso MIT, phần tự soạn trong `resources_src/extra/`).

| Class | Việc |
|---|---|
| `ScriptRoutingTokenizer(Factory)` | Chọn cách tách theo hệ chữ; đánh dấu ranh giới |
| `ThaiSegmenter` | Tách Thái, không cắt giữa cụm ký tự, rút ký tự lặp |
| `SocialNormalizeFilter(Factory)` | Chuẩn hoá token mạng xã hội + slang |
| `CloudPhraseFilter(Factory)` | Gazetteer + n-gram + stopword biên, chỉ phát cụm |
| `CloudFieldsUpdateProcessorFactory` | (Thiết kế cũ, chỉ configset thí nghiệm) tính sẵn cụm/hashtag vào docValues |
| `CloudPatterns` | Regex dùng chung (hashtag, URL, @, tiếng cười, láy số) |

## Chạy

### Chạy thử nhanh (chỉ cần repo này)

Cần JDK 17, Maven 3.9+, Docker, [`uv`](https://docs.astral.sh/uv/). Data test là data SEA **tổng hợp**, tự sinh từ
bộ đáp án `scripts/sea_lexicon*.json` (thư mục `data/` không nằm trong git).

```bash
mvn test                       # 32 test, gồm 49 case SEA trong src/test/resources/cases.tsv
./scripts/deploy_test.sh       # ~2 phút: đóng gói → cài vào bản sao deploy/topic_global → Solr localhost:8986
                               # → sinh data held-out → kiểm tra (in "Kết quả: ĐẠT") → nạp 20k mention/nước + bật pha 2
```

Xong thì mở http://localhost:8986/solr, chọn `topic_sea_id` (hoặc `_ms/_th/_tl/_sg`), xem wordcloud:

```bash
curl "localhost:8986/solr/topic_sea_th/select" -H 'Content-Type: application/json' -d '{"query":"*:*","limit":0,
  "facet":{"cloud":{"type":"terms","field":"search_text_cloud","limit":50}}}'
```

- `deploy/topic_global/` là bản copy configset `topic_global` từ repo team `solr-schemas` (commit `2e11804`,
  17/07/2026). Dùng bản khác: `TOPIC_GLOBAL=<thư mục> ./scripts/deploy_test.sh`.
- `deploy_test.sh` chạy `docker compose down -v`: mỗi lần chạy là xoá sạch data Solr 8986 cũ.
- Thêm so sánh tiếng Việt (`topic_vi_sea`, `topic_vi_vncore`): đặt file export VN qua
  `VN_DATA="<file1> <file2>"` (mặc định `../exported_data_*.json`); `topic_vi_vncore` cần thêm 2 repo cùng cấp
  `../vncore_nlp_research`, `../solr_facet_research`. Thiếu thì script tự bỏ qua phần VN.

### Phòng thí nghiệm (Solr 8985)

```bash
./scripts/build.sh                                  # plugin + configset vào docker/build/ (đối chứng VnCoreNLP nếu có 2 repo trên)
docker compose -f docker/docker-compose.yml up -d   # Solr 9.10.1 ở localhost:8985
./scripts/run_sea_synthetic.sh                      # chấm theo đáp án → results/report_sea_synthetic.md
uv run --with requests scripts/compare_sea_cases.py # 49 case qua analysis API → results/cases_sea.md
```

Core tạo sẵn (`docker/initdb/10-create-cores.sh`, configset chưa build thì bỏ qua): `data_<cc>`/`vocab_<cc>`
(bộ chấm), `sea_{id,ms,th,tl,sg}`, và các core VN thiết kế cũ `vn_*` (cần đối chứng VnCoreNLP + data VN).

## Đánh giá trên data SEA tổng hợp

```bash
./scripts/run_sea_synthetic.sh      # sinh data → nạp data_<cc> → đào từ vựng → nạp vocab_<cc> → chấm điểm
uv run --with pytest pytest scripts/test_phrase_vocab.py
```

- `scripts/sea_lexicon.json`: từ điển sinh data + đáp án (thực thể, cụm chủ đề kèm biến thể slang); `gen_sea_data.py`
  sinh 20k mention/nước (tất định theo seed) vào `data/synthetic/` (gitignore).
- `phrase_vocab.py`: một nguồn cho tỉa cụm con + gộp cửa sổ trượt chồng nhau (cụm dài hơn 4 từ); dùng bởi
  `mine_vocabulary.py`, `compare_vn.py`, `compare_sea_data.py`.
- Core đánh giá dùng `sea_cloud_eval` (= sea_cloud + trường baseline `search_text_icu`, **tắt gazetteer** để không
  "nhắc bài"). Kết quả: `results/report_sea_synthetic.md`.

## Giả định và giới hạn

- `cloud_phrases.txt`, `skip_token_types.txt`, `wdfftypes.txt`… của solr_facet_research bị `.gitignore` chặn nên
  không có; `build.sh` tạo bản thay thế (phrases trống, skip `SINGLE`). Kết quả baseline vì vậy không giống hệt
  bản team từng chạy.
- Gazetteer trong `dict/` chỉ là mẫu demo; bản thật dựng từ Wikidata (CC0) + keyword topic.
- Tiếng Việt qua analyzer mới chỉ tách theo âm tiết rồi ghép n-gram, không có tách từ: nhiều mảnh, cần tỉa cụm con
  ở tầng truy vấn (xem `results/report_vn.md`).
- Stoplist có đụng nghĩa ngay trong một ngôn ngữ (Thái `ถูก` = trợ từ bị động / "rẻ").
- Mới chạy Solr standalone; `${topic.country}` trên SolrCloud chưa kiểm.

## Kết quả lần chạy 22/10/2026 (Solr 9.10.1 standalone, Docker trên macOS)

Chi tiết: `results/report_vn.md` (data VN, topic 10236707) và `results/cases_sea.md` (49 case SEA).

**49 case SEA** (baseline = chain topic_global ICU + ICUFolding + shingle 2–4): baseline 861 cụm, 146 vượt dấu câu,
113 mất dấu Thái; `text_cloud_sea` 145 cụm, 0 vượt dấu câu, 0 mất dấu Thái.

**Data VN, 30k mention giống nhau:**

| core | index doc/s | distinct | facet cold / warm (ms) |
|---|---|---|---|
| vn_vncore (y nguyên solr_facet_research, TextField) | 24.5 | 33 057 | 453 / 15 |
| vn_vncore_dv (cùng analyzer, docValues) | 18.3 | 33 057 | 49 / 20 |
| vn_sea (mọi n-gram 2–4) | 296.5 | 1 825 895 | 722 / 517 |
| vn_sea_vocab (chỉ cụm trong từ vựng đã đào) | 473.0 | 223 518 | 113 / 85 |

**167k mention:** vn_sea_full 4,67 triệu giá trị, facet 7,5 s cold / 3,1 s warm (vượt mục tiêu 5 s);
vn_sea_vocab_full 224k giá trị, 0,70 s / 0,24 s, index nhỏ gần một nửa (452 MB so với 839 MB).

Rút ra:
1. **Không được index mọi n-gram**: số giá trị phân biệt bùng nổ. Phải theo 2 pha — đào từ vựng theo topic
   (`scripts/mine_vocabulary.py`), rồi chỉ index cụm trong từ vựng (`vocabulary=`).
2. **docValues cắt chi phí truy vấn đầu** (453 → 49 ms ở 30k doc) dù cùng analyzer; mức chênh tăng theo số doc.
3. **Tiếng Việt: VnCoreNLP vẫn sạch hơn** ở top 50 (từ ghép đúng). Ghép n-gram theo âm tiết sinh cửa sổ trượt
   trên cụm dài hơn 4 tiếng ("đại hội đại biểu toàn quốc lần thứ xiv" ra "hội đại biểu toàn", "biểu toàn quốc lần").
   Hướng sửa: dùng từ (RDRsegmenter/VnCoreNLP) làm đơn vị cho `CloudPhraseFilter`, và gộp các cửa sổ chồng nhau có
   số đếm gần bằng nhau thành cụm dài.
4. Từ vựng đào ra lớn (224k cụm, 4,9 MB, vượt giới hạn znode 1 MB của ZooKeeper) và hiện đào in-sample; bản thật cần
   job theo topic + nơi lưu ngoài configset.
5. Số index doc/s đo khi nhiều core nạp song song; đo riêng 2 000 doc: analyzer mới 546 doc/s, VnCoreNLP 16 doc/s.

## Kết quả data SEA tổng hợp (22/10/2026)

**Không phải data thật** — 20k mention/nước sinh từ `sea_lexicon.json`. Top 50, recall = số cụm đáp án (≥ 2 từ) có mặt.

| Nước | baseline topic_global: recall / mảnh vụn / trùng | 2 pha (từ vựng): recall / mảnh vụn / trùng | distinct baseline → 2 pha |
|---|---|---|---|
| id | 7/11 · 9 · 2 | **11/11** · 1 · 3 | 183k → 307 |
| ms | 9/10 · 22 · 8 | **10/10** · 1 · 2 | 163k → 260 |
| tl | 9/10 · 16 · 3 | 8/10 · 1 · 0 | 129k → 320 |
| sg | 9/10 · 13 · 3 | **10/10** · 0 · 2 | 138k → 271 |
| th | 0/6 · 0 · 0 (mọi mục là rác: `ลิ ซา`, `ชอป ปี`) | **6/6** · 3 · 0 | 88k → 822 |

Bài học từ lần chạy đầu (recall 2 pha chỉ 7–9/10): stoplist ở biên cụm phải **không chặn từ phủ định**
(`tidak`, `hindi`, `ไม่` — `never_stop.txt`), phải **cho từ nhấn mạnh đứng cuối** (`banget`, `talaga`, `เพราะ`, `มาก` —
`tail_<cc>.txt`), và **không dùng stopwords-iso ms** (lẫn từ nội dung `harga`, `minyak`, `rakyat`); Lucene th có `ส่ง`.
Còn sót ở tl: `ang ganda` (mạo từ `ang` ở đầu) và `asap natin to` (`'to` = "ito" trùng `to` tiếng Anh).
Hạn chế: tỉa/gộp không chạy cho tiếng Thái (cụm ghép không dấu cách nên không tách được từ); gộp cửa sổ chỉ gộp cùng
độ dài (tên 5 từ còn 2 mục); "noise" cao ở mọi cách do bộ sinh ghép từ đệm ngẫu nhiên thành cặp phổ biến.

## Đo lại trên bộ đáp án độc lập (held-out, 22/10/2026)

`LEXICON=scripts/sea_lexicon_holdout.json DATA_DIR=data/holdout REPORT=results/report_sea_holdout.md SEED=7 ./scripts/run_sea_synthetic.sh`

Bộ đáp án `sea_lexicon_holdout.json` do một agent khác viết, không đọc stoplist hay đáp án cũ, chủ đề khác hẳn.
Stoplist **giữ nguyên** từ lần trước (không chỉnh theo kết quả). Script chấm chỉ sửa 1 lỗi: tên Latin 1 từ trong topic
Thái không tính vào đáp án.

| Nước | baseline topic_global | 2 pha | bỏ sót (2 pha) |
|---|---|---|---|
| id | 6/14 | 11/14 | bri liga 1, gak enak*, pesanan belum sampai |
| ms | 6/13 | 12/13 | tak cukup duit* |
| tl | 6/13 | 11/13 | batang quiapo (ra "fpj batang quiapo"), sayang yung lamang |
| sg | 4/12 | 10/12 | so expensive sia (ra "expensive sia"), not worth it (ra "not worth") |
| th | 0/12 | 8/12 | 3 tên/tựa > 4 token hoặc phiên âm bị cắt, หน้าใสขึ้น |
| Tổng | 22/64 (34%) | 52/64 (81%) | |

\* wordcloud có hiện nhưng ở dạng đã chuẩn hoá slang (`tidak enak`, `tidak cukup duit`), chấm nghiêm nên tính sót.
So với bộ đáp án đã dùng để chỉnh stoplist (96%), held-out còn 81%: phần chênh là mức "học tủ".
Lỗi còn lại chủ yếu: stopword ở biên (`so …`, `… it`), luật biên phải có chữ cái (`liga 1`), tiếng Thái không tỉa/gộp được
và tựa > 4 token bị cắt mảnh (29/50 mục top Thái là mảnh vụn).

## Thí nghiệm: bỏ stoplist (22/10/2026)

`sea_cloud_eval` có thêm `text_cloud_sea_nostop` → `cloud_phrases_nostop` (cùng analyzer, stoplist biên trống).
Chấm trên bộ held-out, cả hai đều qua `phrase_vocab.clean` trên 2 000 cụm đầu:

| Nước | có stoplist (2 pha) | KHÔNG stoplist + làm sạch |
|---|---|---|
| id | 11/14 | 12/14 |
| ms | 12/13 | 12/13 |
| tl | 11/13 | 12/13 |
| sg | 10/12 | 12/12 |
| th | 8/12 (29 mảnh vụn) | 8/12 (42 mảnh vụn) |
| Tổng | 52/64 (81%) | 56/64 (88%) |

Không stoplist lấy lại được `so expensive sia`, `worth it`, `train delay again` nhưng lọt nửa cụm `stuck in`,
`chinatown complex market and`, `di gofood dan nikmati`; tiếng Thái nhiều mảnh hơn. Trên 30k mention VN **thật**
(core tạm, đã xoá): top 30 sau làm sạch gần như trùng, không stoplist chỉ thêm `đại hội xiv của`, `của đất nước`.
Số cụm khác nhau trước khi lọc từ vựng tăng ~4–5 lần (61k so với 13k ở id).

## Stoplist tối thiểu (bản dùng thật từ 22/10/2026)

`cloud_stop_<cc>.txt` cho SEA giờ chỉ gồm từ nối theo loại từ ngữ pháp (`resources_src/extra/connectors_*.txt`:
liên từ, giới từ, mạo từ, trợ từ nối; 28–53 mục/nước thay vì 300–1 400). Danh sách lớn cũ giữ ở
`cloud_stop_full_<cc>.txt` chỉ để so. Tiếng Việt giữ danh sách cũ.

| Bộ đáp án | Nước | baseline | tối thiểu | lớn cũ | không stoplist |
|---|---|---|---|---|---|
| held-out 1 (đã xem trước) | id/ms/tl/sg | 22/52 | **48/52** | 44/52 | 48/52 |
| | th | 0/12 | 8/12 | 8/12 | 8/12 |
| held-out 2 (chưa ai xem, chủ đề mới) | id/ms/tl/sg | 20/53 | **47/53** | 43/53 | 49/53 |
| | th | 2/14 | 8/14 | **11/14** | 8/14 |

Tiếng Thái: các cụm bị sót vẫn được tạo, chỉ rớt khỏi top 50 (hạng 53–70 với stoplist tối thiểu, 37–50 với list lớn),
vì bước làm sạch không chạy được cho chữ Thái viết liền nên mảnh vụn (`ร้านเจ๊`, `เจ๊ไฝ`, `ต่อคิว`…) chiếm chỗ.
Khuyến nghị: tiếng Thái tạm dùng list lớn cho tới khi làm sạch chạy được cho Thái.

## Thử thêm từng nhóm từ vào stoplist tối thiểu (22/10/2026)

Nhóm soạn theo loại từ trước khi chạy (`resources_src/extra/groups/`), mỗi nhóm là 1 biến thể trong `sea_cloud_eval`.
Chấm trên 2 bộ held-out; chi tiết mục bị mất khỏi top 50 ở mục "Thêm nhóm từ…" của 2 báo cáo held-out.

| Nhóm | Số đáp án tìm thấy | Mục bị loại khỏi top 50 |
|---|---|---|
| + trợ từ cuối câu (sih, lah, po, เลย…) | không giảm; **Thái held-out 2: 8 → 11/14** | toàn rác/mảnh: `gila sih`, `serius lah`, `บอกเลย` |
| + chỉ định từ (ini, itu, this…) | không giảm | rác: `ini transjakarta`, `hari ini`, `favourite hawker meals this` |
| + trợ động từ/hệ từ (is, sudah, เป็น…) | không giảm | phần lớn rác/mảnh, nhưng chặn `sudah habis stok` (dạng chuẩn hoá của đáp án) |
| + đại từ (aku, kamu, it, ผม…) | **sg held-out 1: 12 → 11/12** | rác ở id/ms, mảnh Thái; nhưng chặn `not worth it`, `worth it` vì "it" |

## Chốt stoplist sau 3 bộ đáp án độc lập (22/10/2026)

Bộ 3 (`sea_lexicon_holdout3.json`, chủ đề mới, chưa ai xem trước) + bộ 1, 2. Cộng dồn số đáp án tìm thấy trong top 50:

| | từ nối + 3 nhóm | **chỉ từ nối** | danh sách lớn cũ | không stoplist | `topic_global` |
|---|---|---|---|---|---|
| id/ms/tl/sg (158 cụm) | 144 | **145** | 132 | 149 | ~60 |
| th (39 cụm) | **26** | 21 | 27 | 21 | 6 |

Chốt: **id/ms/tl/sg chỉ dùng từ nối** (28–54 từ); **th dùng từ nối + trợ từ cuối câu + chỉ định từ + đại từ tiếng Thái**
(59 từ). Với chữ Latin, thêm nhóm không tăng recall và chặn nhầm `lagi gangguan ya` ("ya" là trợ từ). Với tiếng Thái,
bước làm sạch chưa chạy được nên stoplist phải gánh việc dọn mảnh. Bản Thái chốt bỏ nhóm tiếng Anh (this, that…) khỏi
biến thể đã đo — thay đổi nhỏ, chưa đo lại. Bộ dự phòng `sea` (không biết nước) chỉ gồm từ nối.
Không stoplist vẫn có recall cao nhất cho chữ Latin nhưng để lọt nửa cụm (`stuck in`, `… market and`) mà data giả không
đo được — cần người bản xứ chấm top 50 trên data thật trước khi cân nhắc bỏ hẳn.

## Sửa làm sạch cho tiếng Thái (23/10/2026)

`CloudPhraseFilter` nối 2 từ Thái bằng U+200B (zero-width space, `THAI_JOINER`) thay vì ghép liền: người đọc vẫn thấy
`ร้านเจ๊ไฝ`, nhưng `phrase_vocab` tách được từ nên tỉa mảnh / gộp cửa sổ chạy cho tiếng Thái; gazetteer Thái cũng khớp
được (dòng `ลิซ่า แบล็กพิงก์` trong `cloud_names_th.txt`). Chấm Thái so đáp án viết liền nên script bỏ U+200B khi so.

Tiếng Thái trên 3 bộ held-out (39 cụm): trước khi sửa 26/39 → **sau khi sửa 35/39**; chỉ từ nối 34/39; list lớn cũ 29/39;
`topic_global` 6/39. Mảnh vụn trong top 50 Thái ở bộ 1 giảm từ 42 xuống 3. Chữ Latin không đổi (145/158).
Còn sót: tựa/tên Thái dài hơn 4 từ (`แฟนผมเป็นประธานนักเรียน`, `รถไฟฟ้ามหานครสายเฉลิมรัชมงคล`) và tên phiên âm
(`เจมีไนน์โฟร์ท`) — cần gazetteer.
Lưu ý tích hợp: giá trị facet Thái chứa U+200B; UI hiển thị bình thường, nhưng export CSV/so khớp chuỗi phía backend
nên bỏ U+200B (giữ nguyên khi gửi lại làm filter, vì đó là giá trị thật trong index).

## Export / import vào configset khác (topic_global)

```bash
./scripts/package.sh        # -> dist/sea-cloud-0.1.0.tar.gz (jar + conf/lang + conf/dict + snippets + installer + INSTALL.md)
./scripts/deploy_test.sh    # cài gói vào BẢN SAO solr-schemas/topic_global, chạy Solr ở 8986, tự kiểm tra
uv run --with requests python scripts/compare_deploy_vn.py   # so tiếng Việt với configset solr_facet_research
```

Hướng dẫn cài cho team: `deploy/INSTALL.md` (đi kèm trong gói). `install_into_configset.py` chỉ thêm fieldType,
2 trường và processor (vào mọi chain có RunUpdate: `updateconfig`, `tolerant` của topic_global), lưu `*.bak-sea-cloud`,
chạy lại nhiều lần vẫn an toàn. Kết quả kiểm tra: `results/deploy_test.md` (ĐẠT: core load, schema chỉ thêm, tìm kiếm
giống bản gốc, có wordcloud 5 nước, atomic update) và `results/deploy_vn.md`.

Collection trong Solr thử (8986): `topic_global_orig` (bản gốc, đối chứng), `topic_sea_{id,ms,th,tl,sg}` (20k mention
tổng hợp/nước), `topic_sea_default`, `topic_vi_sea` + `topic_vi_vncore` (cùng 40k mention VN thật),
`topic_vi_sea_full` (2 file export, 458 232 mention gửi lên → 326 525 sau `SkipExistingDocuments` của topic_global).
Lưu ý: bản cài chưa bật từ vựng (pha 2), nên ở 326k mention facet mất 4,2 s lần đầu / 3,1 s lặp lại — cần pha 2.

## Thử kiểu solr_facet_research: copyField + TextField `search_text_cloud` (23/10/2026)

Core thử `topic_tf_vi` (40k) và `topic_tf_vi_full` (326k) ở cổng 8986 = topic_global_sea + `search_text_cloud`
(type `text_cloud_sea`) + `copyField search_text → search_text_cloud`. Cùng core nên so được 2 trường trên cùng data:

| | 40k: TextField `search_text_cloud` | 40k: docValues `cloud_phrases` | 326k: TextField | 326k: docValues |
|---|---|---|---|---|
| Lần đầu sau mỗi commit/reload | 4,2 s | 0,7 s | **17,1 s** | 5,6 s |
| Lặp lại (cùng searcher) | 34 ms | 212 ms | 53 ms | 3,3 s |

TextField phải un-invert vào heap: chậm ở lần đầu sau MỖI commit (mention đổ vào liên tục → commit thường xuyên),
nhanh khi lặp lại; heap dùng 3,2/4,3 GB. Top cụm giống hệt. Cả hai đều quá chậm khi index mọi n-gram (5,6 triệu
giá trị) → cần pha 2 (từ vựng). Ghi chú: loader rút `search_text` về ["", phần tử 2] nên thí nghiệm này không thấy
khác biệt BR-27 (copyField lấy mọi phần tử).

## Chuyển hẳn sang copyField + TextField `search_text_cloud` (23/10/2026)

Bản dùng thật giờ giống solr_facet_research: `copyField search_text → search_text_cloud` (type `text_cloud_sea`),
cụm + hashtag (`#…`, tokenizer `emitHashtags="true"`) chung 1 trường, không còn processor (script cài không đụng
solrconfig trừ `--warm`). Mất BR-27 (copyField lấy mọi phần tử `search_text`). Lọc theo cụm phải dùng
`{!term f=search_text_cloud}…`. `CloudFieldsUpdateProcessorFactory` và các trường `cloud_phrases`/`cloud_hashtags` chỉ
còn dùng cho configset thí nghiệm. Sửa kèm: hashtag từng làm offset lùi khi index vào TextField (test hồi quy
`offsetsNeverGoBackwardsWithHashtags`). Số đo khi nạp liên tục: `results/deploy_live.md` — **bắt buộc pha 2** cho topic lớn.

## Gộp collection trong Solr thử (25/10/2026)

`deploy_test.sh` giờ tạo đúng 8 collection, đều chạy thiết kế chốt (copyField + TextField + warming + pha 2):
`topic_global_orig` (bản gốc đối chứng), `topic_sea_{id,ms,th,tl,sg}` (1 topic/nước, 20k mention tổng hợp),
`topic_vi_sea` + `topic_vi_vncore` (cùng 40k mention VN thật, so với solr_facet_research). Pha 2 bật bằng
`scripts/enable_vocab.sh` (nạp → đào từ vựng → gắn `cloud.vocabulary` → nạp lại). Core đo hiệu năng
(`deploy_measure_vn.sh`) là core tạm, tự xoá khi xong. Bỏ: `topic_sea_default` (unit test đã kiểm bộ `sea`),
các core thí nghiệm `*_full`, `*_nowarm`, `topic_vi_vocab_full`, `topic_tf_*`.
Tiếng Việt 40k, pha 2: 27 480 cụm (VnCoreNLP 30 368), facet lần đầu 249 ms / lặp lại 6 ms (VnCoreNLP 98 / 7 ms),
index 821 mention/s (VnCoreNLP 57). Chi tiết: `results/deploy_vn.md`.

## So tách từ tiếng Thái với PyThaiNLP, Lucene, ICU (26/10/2026)

`scripts/compare_thai_seg.py` (+ `scripts/ThaiTokenDump.java` chạy các tokenizer Java) trên 53 650 câu Thái tổng hợp
(3 bộ held-out + `cases.tsv`). Không có gold thương mại được, nên đo khớp ranh giới với newmm (chỉ là mốc) và
đáp án `truth_th.json` (cụm có bị cắt đúng 2 mép không). ThaiSegmenter khớp newmm F1 0,977; cắt đúng mép 96,0%
(newmm 94,3%, ICU 88,6%, Lucene ThaiTokenizer 67,4%); token rác 21,9/1000 (newmm 62,1); nhanh hơn newmm ~4 lần.
Data tổng hợp có ít từ (377 từ khác nhau) nên cần đo lại trên data Thái thật. Chi tiết: `results/compare_thai_seg.md`.

Đã sửa 3 lỗi của ThaiSegmenter mà lần đo này tìm ra (`ThaiSegmenter.tokenize`, test hồi quy trong `ThaiSegmenterTest`):
1. Đuôi câm theo luật TCC (1–2 phụ âm, có thể kèm ิ/ุ, rồi ์) luôn dính cụm trước: `วิ|ชญ์` → `วิชญ์`, `รน|ต์` → `รนต์`.
2. Kéo dài 2 ký tự: ký tự lẻ giống ký tự cuối từ trước được gộp vào từ đó (`สายย` → `สาย`); dấu/nguyên âm lặp ≥ 2 rút còn 1.
3. Phụ âm lặp ≥ 3 rút còn 1 nhưng "dùng chung" được cho từ sau (`ขึ้นนนนี้` → `ขึ้น` + `นี้`, trước đây `ขึ้|นนนนี้`);
   không giữ 2 ký tự vì `มากก` sẽ thành `มา|กก`; hoà điểm thì ưu tiên dùng chung (`มากกกว่า` → `มาก` + `กว่า`).
   Chữ số Thái không bị rút (`๒๐๐๐` từng thành `๒๐`).

| ThaiSegmenter | Trước | Sau |
|---|---|---|
| Cụm đáp án cắt đúng 2 mép | 96,0% | 97,0% (newmm 94,3%) |
| Đúng mép và ≤ 4 token | 82,5% | **87,8%** (newmm 85,6%) |
| Token rác / 1000 | 21,9 | **9,4** (newmm 62,1) |
| F1 so với newmm | 0,977 | 0,962 |

F1 giảm vì 33 092/33 400 ranh giới newmm có mà gói không có nằm **trong** chuỗi chữ kéo dài (newmm cắt `ขึ้น|นน`).
Còn lại: tên/sai chính tả không có trong từ điển (`โฟร์|ท`, `แช|ม`) và chỗ hoà điểm 2 từ (`เยอะนะ` → `เย|อะนะ`, newmm
cũng vậy; cần tần suất từ để sửa). Lỗi cũ chưa sửa: 3 phụ âm liền nhau hợp lệ ở chỗ nối 2 từ (`ถนนนี้` → `ถ|นี้`,
`หมอออกมา` → `หมอก|มา`) bị coi là chữ kéo dài; tách đúng cần tần suất từ vì `มากกก` (kéo dài) và `หมอออก` (nối từ)
giống hệt nhau về hình thức. Solr 8986 vẫn chạy jar cũ cho tới lần `deploy_test.sh` sau.
