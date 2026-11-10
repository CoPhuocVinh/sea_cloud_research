# Cài plugin wordcloud SEA vào Solr

Gói này thêm wordcloud cụm 2–4 từ + hashtag cho topic Indonesia, Malaysia, Thái Lan, Philippines, Singapore vào một
configset có sẵn (vd. `topic_global`), **giống cách `solr_facet_research` làm cho tiếng Việt**:
`copyField search_text → search_text_cloud` (TextField) và facet trên `search_text_cloud`. Chỉ **thêm** fieldType,
1 trường và 1 copyField (và tuỳ chọn listener warming); không sửa trường hay chain có sẵn, nên tìm kiếm không đổi.

## Trong gói có gì

| Đường dẫn | Là gì |
|---|---|
| `lib/sea-cloud-analysis-<ver>.jar` | Plugin (Java 11+, Lucene 9.12 / Solr 9.10). Từ điển Thái (PyThaiNLP, CC0) nằm sẵn trong jar |
| `conf/lang/cloud_stop_<nước>.txt` | Từ nối chặn ở đầu/cuối cụm (28–54 từ/nước) |
| `conf/lang/cloud_slang_<nước>.txt`, `cloud_tail_<nước>.txt` | Slang → dạng chuẩn; từ nhấn được đứng cuối cụm |
| `conf/dict/cloud_names_<nước>.txt`, `thai_extra.txt` | Gazetteer tên riêng (mẫu); từ Thái bổ sung (thương hiệu, tên) |
| `snippets/*.xml` | Đoạn cấu hình sẽ được chèn (để xem trước) |
| `install_into_configset.py` | Script cài (Python 3.9+, không cần thư viện ngoài) |

`<nước>` = `id`, `ms`, `th`, `tl`, `sg`, `sea` (dự phòng khi chưa khai báo nước), `vi` (chỉ để thử).

## Yêu cầu

- Solr 9.10.x, bật module ICU: biến môi trường `SOLR_MODULES=analysis-extras` trên mọi node.
- Collection biết nước qua core property `topic.country` (bước 3). Thiếu thì dùng bộ `sea`.

## Các bước

```bash
# 1. Cài vào bản copy của configset (không sửa thẳng bản đang chạy)
cp -R topic_global topic_global_sea
python3 install_into_configset.py topic_global_sea --warm              # SolrCloud
python3 install_into_configset.py topic_global_sea --warm --with-lib   # standalone: jar vào topic_global_sea/lib
```

Script in ra những gì đã thêm và lưu bản gốc thành `*.bak-sea-cloud`; chạy lại không thêm trùng.
`--warm` thêm listener `newSearcher`/`firstSearcher` vào `<query>` của `solrconfig.xml`: sau mỗi commit Solr dựng sẵn
bộ đếm facet (un-invert `search_text_cloud`) trước khi chuyển truy vấn sang searcher mới.

**2. Đặt jar**
- Standalone / `precreate-core`: dùng `--with-lib` (Solr tự nạp `<core>/lib/*.jar`).
- SolrCloud: jar **không** đưa vào ZooKeeper được. Copy jar vào thư mục `sharedLib` (khai báo trong `solr.xml`) trên
  **mọi node** rồi rolling restart, trước khi upload configset.

**3. Khai báo nước cho từng collection**
- SolrCloud: `/admin/collections?action=CREATE&name=topic_123&collection.configName=topic_global_sea&property.topic.country=th`
- Standalone: thêm dòng `topic.country=th` vào `<core>/core.properties` rồi reload core.

**4. Upload configset** (SolrCloud): `bin/solr zk upconfig -n topic_global_sea -d topic_global_sea/conf -z <zk>`

## Truy vấn wordcloud

```bash
# Top cụm + hashtag (hashtag bắt đầu bằng "#")
curl "$SOLR/<core>/select" -H 'Content-Type: application/json' -d '{"query":"*:*","limit":0,
  "facet":{"cloud":{"type":"terms","field":"search_text_cloud","limit":100}}}'
# Chỉ hashtag
  ... "facet":{"tags":{"type":"terms","field":"search_text_cloud","prefix":"#","limit":20}}
# Bấm vào 1 cụm để lọc mention: PHẢI dùng {!term}, không dùng search_text_cloud:"..." (sẽ bị tách lại thành cụm)
curl "$SOLR/<core>/select" --data-urlencode 'q=*:*' --data-urlencode 'fq={!term f=search_text_cloud}harga murah'
```

Trên Solr Admin → Query: `q=*:*`, `rows=0`, tick `facet`, `facet.field=search_text_cloud`, Raw Query Parameters
`facet.limit=50&facet.mincount=1`.

## Lưu ý

- **BR-27 không đảm bảo**: `copyField` lấy MỌI phần tử của `search_text` (gồm cả nội dung bóc từ ảnh/video nếu có),
  không chỉ phần tử số 2. Muốn đúng BR-27 thì pipeline phải gửi phần tử số 2 vào một trường riêng làm nguồn copyField.
- Chỉ mention được index **sau** khi cài mới có `search_text_cloud`; mention cũ cần index lại.
- Facet TextField phải un-invert trường vào heap ở **mỗi searcher mới** (topic_global soft commit 5 s). Với topic lớn
  cần bật lọc từ vựng (pha 2: `property.cloud.vocabulary=dict/cloud_vocab_<topic>.txt`) để số cụm nhỏ; xem
  `results/deploy_live.md` của repo `sea_cloud_research` để biết số đo.
- Cụm tiếng Thái nối các từ bằng U+200B (vô hình). UI hiển thị bình thường; export CSV nên bỏ ký tự này; khi lọc thì gửi
  nguyên giá trị (có U+200B).
- Gỡ: khôi phục `*.bak-sea-cloud`, xoá jar, reload.
