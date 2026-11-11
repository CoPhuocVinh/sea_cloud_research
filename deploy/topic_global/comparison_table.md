# So sánh solrconfig.xml và solrconfig9.xml

| STT | Mục | solrconfig.xml | solrconfig9.xml | Ghi chú |
|-----|-----|----------------|-----------------|---------|
| 1 | **Comment Header URL** | `http://wiki.apache.org/solr/SolrConfigXml` | `https://solr.apache.org/guide/solr/latest/configuration-guide/configuring-solrconfig-xml.html` | URL mới hơn, HTTPS |
| 2 | **directoryFactory** | Có thẻ đóng riêng `</directoryFactory>` | Self-closing tag | Format khác nhau, chức năng giống nhau |
| 3 | **schemaFactory** | ✅ Có cấu hình `ManagedIndexSchemaFactory` | ❌ Không có | solrconfig.xml có cấu hình schema factory |
| 4 | **indexConfig - infoStream** | ✅ `<infoStream>true</infoStream>` | ❌ Commented out | solrconfig.xml bật infoStream |
| 5 | **indexConfig - Comments** | Ít comment chi tiết | Nhiều comment chi tiết về merge policy, deletion policy | solrconfig9.xml có nhiều tài liệu hơn |
| 6 | **JMX** | ✅ Có `<jmx />` | ❌ Không có | solrconfig.xml có JMX config |
| 7 | **autoCommit** | `<maxDocs>1000</maxDocs>` + `<maxTime>30000</maxTime>` | Chỉ có `<maxTime>${solr.autoCommit.maxTime:15000}</maxTime>` | solrconfig.xml có maxDocs |
| 8 | **autoSoftCommit** | `<maxDocs>1000</maxDocs>` + `<maxTime>500</maxTime>` | Chỉ có `<maxTime>${solr.autoSoftCommit.maxTime:3000}</maxTime>` | solrconfig.xml có maxDocs |
| 9 | **maxBooleanClauses** | `2048` (hardcoded) | `${solr.max.booleanClauses:1024}` (variable) | solrconfig9.xml dùng biến môi trường |
| 10 | **minPrefixQueryTermLength** | ❌ Không có | ✅ `${solr.query.minPrefixLength:-1}` | Chỉ có trong solrconfig9.xml |
| 11 | **Cache Comments** | Nói về LRUCache, FastLRUCache | Nói về CaffeineCache (Solr 9.0+) | Comments phản ánh version |
| 12 | **Query Listeners** | ❌ Không có | ✅ Có `newSearcher` và `firstSearcher` listeners | solrconfig9.xml có query warming |
| 13 | **slowQueryThresholdMillis** | ✅ `5000` | ❌ Không có | Custom config trong solrconfig.xml |
| 14 | **requestDispatcher - handleSelect** | ✅ `handleSelect="false"` | ❌ Không có attribute | solrconfig.xml có explicit config |
| 15 | **requestParsers** | ✅ Có `enableRemoteStreaming="true"` | ❌ Commented out | solrconfig.xml bật remote streaming |
| 16 | **requestParsers - limits** | `multipartUploadLimitInKB="2048000"` | Commented, default `-1` | solrconfig.xml có giới hạn cụ thể |
| 17 | **/select handler - defaults** | `df="search_text"` | Không có `df` | solrconfig.xml có default field |
| 18 | **/query handler - defaults** | `df="search_text"` | Không có `df` | solrconfig.xml có default field |
| 19 | **initParams path** | `/update/**,/query,/select,/tvrh,/elevate,/spell` | `/update/**,/query,/select,/spell` | solrconfig.xml có thêm `/tvrh,/elevate` |
| 20 | **initParams - df** | `df="search_text"` | `df="_text_"` | Default field khác nhau |
| 21 | **Search Components** | Chỉ có `terms` component | Có `terms`, `spellcheck`, `highlight` | solrconfig9.xml có nhiều components hơn |
| 22 | **SpellCheck Component** | ❌ Không có | ✅ Có đầy đủ config | Chỉ có trong solrconfig9.xml |
| 23 | **SpellCheck Handler** | ❌ Không có | ✅ Có `/spell` handler | Chỉ có trong solrconfig9.xml |
| 24 | **Highlight Component** | ❌ Không có | ✅ Có đầy đủ config | Chỉ có trong solrconfig9.xml |
| 25 | **Admin Config** | ✅ `<admin><defaultQuery>*:*</defaultQuery></admin>` | ❌ Không có | solrconfig.xml có admin config |
| 26 | **Update Request Processor Chains** | Custom chains: `updateconfig`, `tolerant` | Default chain: `add-unknown-fields-to-the-schema` | Khác nhau về strategy |
| 27 | **SkipExistingDocumentsProcessor** | ✅ Có trong `updateconfig` chain | ❌ Không có | Custom processor trong solrconfig.xml |
| 28 | **Update Processors (Schemaless)** | ❌ Không có | ✅ Có đầy đủ: UUID, RemoveBlank, FieldNameMutating, Parse*, AddSchemaFields | solrconfig9.xml hỗ trợ schemaless mode |
| 29 | **/update handler** | ✅ Có với custom chain | ❌ Không có explicit config | solrconfig.xml có custom update handler |
| 30 | **/update/json handler** | ✅ Có | ❌ Không có | Chỉ có trong solrconfig.xml |
| 31 | **TolerantUpdateProcessor** | ✅ Có chain `tolerant` | ❌ Không có | Custom error handling trong solrconfig.xml |
| 32 | **Query Response Writer** | Commented JSON writer | Không có | Cả hai đều không active |
| 33 | **Total Lines** | 661 dòng | 1026 dòng | solrconfig9.xml dài hơn nhiều |

## Tóm tắt chính:

### solrconfig.xml (File hiện tại - đã sửa cache):
- ✅ Có schemaFactory config
- ✅ Có JMX config
- ✅ Có custom update processor chains
- ✅ Có admin config
- ✅ Có slow query logging
- ✅ Có remote streaming enabled
- ✅ Default field: `search_text`
- ❌ Thiếu các search components mới (spellcheck, highlight)
- ❌ Thiếu schemaless mode processors
- ❌ Thiếu query listeners

### solrconfig9.xml (File template Solr 9):
- ✅ Có đầy đủ search components (spellcheck, highlight)
- ✅ Có schemaless mode processors
- ✅ Có query listeners cho cache warming
- ✅ Có minPrefixQueryTermLength
- ✅ Dùng biến môi trường cho config
- ✅ Default field: `_text_`
- ❌ Không có JMX
- ❌ Không có custom update chains
- ❌ Không có admin config
- ❌ Không có remote streaming

