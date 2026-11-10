# Wordcloud trên data SEA TỔNG HỢP: baseline topic_global vs analyzer mới

Sinh bởi `scripts/compare_sea_data.py`. Data: `data/holdout2` (sinh bởi `scripts/gen_sea_data.py`, seed cố định). **Không phải data thật.** Gazetteer tắt ở mọi core đánh giá.

Chấm trên top 50: hit / dup / fragment / noise (số mục), recall = số cụm đáp án (≥ 2 từ) có mặt.

| Nước | Cách | distinct | recall | hit | dup | fragment | noise |
|---|---|---|---|---|---|---|---|
| id | baseline topic_global | 171612 | 5/14 | 5 | 2 | 12 | 31 |
| id | 2 pha (từ vựng) | 419 | 11/14 | 11 | 6 | 0 | 33 |
| id | stoplist dùng thật + làm sạch | 39710 | 11/14 | 11 | 6 | 0 | 33 |
| id | chỉ từ nối + làm sạch | 39710 | 11/14 | 11 | 6 | 0 | 33 |
| id | stoplist lớn cũ + làm sạch | 8260 | 10/14 | 10 | 5 | 4 | 31 |
| id | không stoplist + làm sạch | 56957 | 11/14 | 11 | 6 | 0 | 33 |
| ms | baseline topic_global | 175567 | 5/13 | 5 | 1 | 14 | 30 |
| ms | 2 pha (từ vựng) | 410 | 12/13 | 12 | 5 | 1 | 32 |
| ms | stoplist dùng thật + làm sạch | 48109 | 12/13 | 12 | 5 | 1 | 32 |
| ms | chỉ từ nối + làm sạch | 48109 | 12/13 | 12 | 5 | 1 | 32 |
| ms | stoplist lớn cũ + làm sạch | 14951 | 10/13 | 10 | 4 | 4 | 32 |
| ms | không stoplist + làm sạch | 60842 | 12/13 | 12 | 5 | 1 | 32 |
| tl | baseline topic_global | 177549 | 5/13 | 5 | 3 | 15 | 27 |
| tl | 2 pha (từ vựng) | 543 | 12/13 | 12 | 9 | 5 | 24 |
| tl | stoplist dùng thật + làm sạch | 48817 | 12/13 | 12 | 9 | 5 | 24 |
| tl | chỉ từ nối + làm sạch | 48817 | 12/13 | 12 | 9 | 5 | 24 |
| tl | stoplist lớn cũ + làm sạch | 14287 | 12/13 | 12 | 8 | 3 | 27 |
| tl | không stoplist + làm sạch | 61194 | 13/13 | 13 | 9 | 4 | 24 |
| sg | baseline topic_global | 173004 | 5/13 | 5 | 3 | 20 | 22 |
| sg | 2 pha (từ vựng) | 496 | 12/13 | 12 | 7 | 6 | 25 |
| sg | stoplist dùng thật + làm sạch | 53631 | 12/13 | 12 | 7 | 6 | 25 |
| sg | chỉ từ nối + làm sạch | 53631 | 12/13 | 12 | 7 | 6 | 25 |
| sg | stoplist lớn cũ + làm sạch | 22143 | 11/13 | 11 | 7 | 5 | 27 |
| sg | không stoplist + làm sạch | 57696 | 13/13 | 13 | 8 | 2 | 27 |
| th | baseline topic_global | 180349 | 2/14 | 2 | 0 | 1 | 47 |
| th | 2 pha (từ vựng) | 472 | 13/14 | 13 | 5 | 4 | 28 |
| th | stoplist dùng thật + làm sạch | 46861 | 13/14 | 13 | 5 | 4 | 28 |
| th | chỉ từ nối + làm sạch | 58892 | 13/14 | 13 | 6 | 4 | 27 |
| th | stoplist lớn cũ + làm sạch | 22087 | 11/14 | 11 | 4 | 7 | 28 |
| th | không stoplist + làm sạch | 67930 | 13/14 | 13 | 6 | 4 | 27 |

## Cụm lọt vào nhờ luật nới (phủ định / từ nhấn cuối cụm)

Đo phần hại của luật nới: cụm nào trong top 50 của 2 pha chỉ có mặt nhờ luật đó, và nó là đáp án hay rác.

| Nước | Cụm (mention) trong top 50 của 2 pha | Lọt nhờ luật | Là |
|---|---|---|---|
| id | tidak sabar banget (1961) | phủ định 'tidak' | noise |
| id | penuh banget (1863) | từ cuối 'banget' | đáp án |
| id | tidak dapet duduk (1660) | phủ định 'tidak' | noise |
| id | penuhh banget (880) | từ cuối 'banget' | đáp án |
| id | tidak dapat duduk (836) | phủ định 'tidak' | noise |
| id | jakarta tidak sabar banget (331) | từ cuối 'banget' | noise |
| id | jakarta penuh banget (311) | từ cuối 'banget' | noise |
| ms | tidak berbaloi (2077) | phủ định 'tidak' | noise |
| ms | tidak berbaloi lgsg (1082) | phủ định 'tidak' | noise |
| ms | tidak berbaloi langsung (1048) | phủ định 'tidak' | noise |
| ms | sedapp gila (985) | từ cuối 'gila' | đáp án |
| ms | sdp gila (934) | từ cuối 'gila' | đáp án |
| tl | baha na naman (1287) | từ cuối 'naman' | đáp án |
| sg | cannot get (1881) | phủ định 'cannot' | fragment |
| sg | no agent fee (1606) | phủ định 'no' | noise |
| sg | cannot get tix (987) | phủ định 'cannot' | đáp án |
| sg | cannot get tickets (938) | phủ định 'cannot' | đáp án |
| th | รถติด​มาก (1384) | từ cuối 'มาก' | đáp án |
| th | คน​เยอะ​มาก (1025) | từ cuối 'มาก' | đáp án |
| th | ไม่​คุ้ม​เลย​ย (940) | phủ định 'ไม่' | đáp án |
| th | อร่อย​มาก (818) | từ cuối 'มาก' | đáp án |

## Top 15 theo nước

### id

Cụm đáp án mà **2 pha** bỏ sót: nggak dapet duduk, nggak sabar banget, naik mrt aja

| # | baseline topic_global | 2 pha (từ vựng) | stoplist dùng thật + làm sạch | chỉ từ nối + làm sạch | stoplist lớn cũ + làm sạch | không stoplist + làm sạch |
|---|---|---|---|---|---|---|
| 1 | blackpink world (2933) | blackpink world tour born (2933) | blackpink world tour born (2933) | blackpink world tour born (2933) | blackpink world tour born (2933) | blackpink world tour born (2933) |
| 2 | blackpink world tour (2933) | krl commuterline (2863) | krl commuterline (2863) | krl commuterline (2863) | krl commuterline (2863) | krl commuterline (2863) |
| 3 | blackpink world tour born (2933) | mrt jakarta (2632) | mrt jakarta (2632) | mrt jakarta (2632) | mrt jakarta (2632) | mrt jakarta (2632) |
| 4 | born pink (2933) | gelora bung karno (2197) | gelora bung karno (2197) | gelora bung karno (2197) | gelora bung karno (2197) | gelora bung karno (2197) |
| 5 | born pink jakarta (2933) | stasiun manggarai (2156) | stasiun manggarai (2156) | stasiun manggarai (2156) | stasiun manggarai (2156) | stasiun manggarai (2156) |
| 6 | pink jakarta (2933) | tidak sabar banget (1961) | tidak sabar banget (1961) | tidak sabar banget (1961) | tidak sabar banget (1961) | tidak sabar banget (1961) |
| 7 | tour born (2933) | penuh banget (1863) | penuh banget (1863) | penuh banget (1863) | penuh banget (1863) | penuh banget (1863) |
| 8 | tour born pink (2933) | tidak dapet duduk (1660) | tidak dapet duduk (1660) | tidak dapet duduk (1660) | tidak dapet duduk (1660) | tidak dapet duduk (1660) |
| 9 | tour born pink jakarta (2933) | buat perjalanan transjakarta (1587) | buat perjalanan transjakarta (1587) | buat perjalanan transjakarta (1587) | cashback 20 buat perjalanan (1587) | buat perjalanan transjakarta (1587) |
| 10 | world tour (2933) | cashback 20 buat perjalanan (1587) | cashback 20 buat perjalanan (1587) | cashback 20 buat perjalanan (1587) | cek di bit (1587) | cashback 20 buat perjalanan (1587) |
| 11 | world tour born (2933) | cek di bit (1587) | cek di bit (1587) | cek di bit (1587) | dapatkan cashback (1587) | cek di bit (1587) |
| 12 | world tour born pink (2933) | kamu sekarang dan dapatkan (1587) | kamu sekarang dan dapatkan (1587) | kamu sekarang dan dapatkan (1587) | kartu uang elektronik (1587) | elektronik kamu sekarang dan (1587) |
| 13 | krl commuterline (2863) | kartu uang elektronik kamu (1587) | kartu uang elektronik kamu (1587) | kartu uang elektronik kamu (1587) | ly promo naik tj (1587) | ly promo naik tj (1587) |
| 14 | mrt jakarta (2632) | ly promo naik tj (1587) | ly promo naik tj (1587) | ly promo naik tj (1587) | perjalanan transjakarta (1587) | promo spesial (1587) |
| 15 | bung karno (2197) | promo spesial (1587) | promo spesial (1587) | promo spesial (1587) | promo spesial (1587) | halte bundaran hi (1472) |

### ms

Cụm đáp án mà **2 pha** bỏ sót: tak berbaloi langsung

| # | baseline topic_global | 2 pha (từ vựng) | stoplist dùng thật + làm sạch | chỉ từ nối + làm sạch | stoplist lớn cũ + làm sạch | không stoplist + làm sạch |
|---|---|---|---|---|---|---|
| 1 | pelajaran malaysia (6082) | sijil pelajaran malaysia (6082) | sijil pelajaran malaysia (6082) | sijil pelajaran malaysia (6082) | sijil pelajaran malaysia (6082) | sijil pelajaran malaysia (6082) |
| 2 | sijil pelajaran (6082) | coklat dubai (5420) | coklat dubai (5420) | coklat dubai (5420) | coklat dubai (5420) | coklat dubai (5420) |
| 3 | sijil pelajaran malaysia (6082) | keputusan sijil pelajaran malaysia (3412) | keputusan sijil pelajaran malaysia (3412) | keputusan sijil pelajaran malaysia (3412) | keputusan sijil pelajaran malaysia (3412) | keputusan sijil pelajaran malaysia (3412) |
| 4 | coklat dubai (5420) | kementerian pendidikan malaysia (2603) | kementerian pendidikan malaysia (2603) | kementerian pendidikan malaysia (2603) | kementerian pendidikan malaysia (2603) | kementerian pendidikan malaysia (2603) |
| 5 | keputusan sijil (3412) | nak try (2378) | nak try (2378) | nak try (2378) | nasi kandar line clear (2191) | nak try (2378) |
| 6 | keputusan sijil pelajaran (3412) | nasi kandar line clear (2191) | nasi kandar line clear (2191) | nasi kandar line clear (2191) | tidak berbaloi (2077) | nasi kandar line clear (2191) |
| 7 | keputusan sijil pelajaran malaysia (3412) | tidak berbaloi (2077) | tidak berbaloi (2077) | tidak berbaloi (2077) | coklat dubai edisi terhad (1610) | tidak berbaloi (2077) |
| 8 | malaysia 2025 (3412) | beli 2 percuma (1610) | beli 2 percuma (1610) | beli 2 percuma (1610) | ly coklat dubai promo (1610) | beli 2 percuma (1610) |
| 9 | pelajaran malaysia 2025 (3412) | coklat dubai edisi terhad (1610) | coklat dubai edisi terhad (1610) | coklat dubai edisi terhad (1610) | order sekarang di bit (1610) | coklat dubai edisi terhad (1610) |
| 10 | sijil pelajaran malaysia 2025 (3412) | ly coklat dubai promo (1610) | ly coklat dubai promo (1610) | ly coklat dubai promo (1610) | semoga dipermudahkn (1314) | ly coklat dubai promo (1610) |
| 11 | kementerian pendidikan (2603) | order sekarang di bit (1610) | order sekarang di bit (1610) | order sekarang di bit (1610) | smoga dipermudahkan (1241) | order sekarang di bit (1610) |
| 12 | kementerian pendidikan malaysia (2603) | percuma 1 sepanjang minggu (1610) | percuma 1 sepanjang minggu (1610) | percuma 1 sepanjang minggu (1610) | beratur panjang (1104) | percuma 1 sepanjang minggu (1610) |
| 13 | pendidikan malaysia (2603) | sepanjang minggu ni (1610) | sepanjang minggu ni (1610) | sepanjang minggu ni (1610) | tidak berbaloi lgsg (1082) | sepanjang minggu ni (1610) |
| 14 | kandar line (2191) | hari ni (1515) | hari ni (1515) | hari ni (1515) | tidak berbaloi langsung (1048) | hari ni (1515) |
| 15 | kandar line clear (2191) | serius lah (1477) | serius lah (1477) | serius lah (1477) | beratur pjg (1038) | serius lah (1477) |

### tl

Cụm đáp án mà **2 pha** bỏ sót: ang lakas ng ulan

| # | baseline topic_global | 2 pha (từ vựng) | stoplist dùng thật + làm sạch | chỉ từ nối + làm sạch | stoplist lớn cũ + làm sạch | không stoplist + làm sạch |
|---|---|---|---|---|---|---|
| 1 | jolly spaghetti (3461) | jolly spaghetti (3461) | jolly spaghetti (3461) | jolly spaghetti (3461) | jolly spaghetti (3461) | jolly spaghetti (3461) |
| 2 | bagyong kristine (3203) | bagyong kristine (3203) | bagyong kristine (3203) | bagyong kristine (3203) | bagyong kristine (3203) | bagyong kristine (3203) |
| 3 | ng ulan (2544) | metro manila (2433) | metro manila (2433) | metro manila (2433) | metro manila (2433) | ng ulan (2544) |
| 4 | metro manila (2433) | ingat po (2252) | ingat po (2252) | ingat po (2252) | stay safe (2157) | metro manila (2433) |
| 5 | ingat po (2252) | stay safe (2157) | stay safe (2157) | stay safe (2157) | marikina river (2027) | ingat po (2252) |
| 6 | stay safe (2157) | marikina river (2027) | marikina river (2027) | marikina river (2027) | national disaster risk reduction (1546) | stay safe (2157) |
| 7 | marikina river (2027) | chickenjoy is (1594) | chickenjoy is (1594) | chickenjoy is (1594) | reduction and management council (1546) | marikina river (2027) |
| 8 | chickenjoy is (1594) | national disaster risk reduction (1546) | national disaster risk reduction (1546) | national disaster risk reduction (1546) | bucket sa jollibee app (1491) | chickenjoy is (1594) |
| 9 | sa jollibee (1554) | reduction and management council (1546) | reduction and management council (1546) | reduction and management council (1546) | delivery ngayong tag ulan (1491) | disaster risk reduction and (1546) |
| 10 | and management (1546) | bucket sa jollibee app (1491) | bucket sa jollibee app (1491) | bucket sa jollibee app (1491) | free jolly spaghetti (1491) | app at makakuha ng (1491) |
| 11 | and management council (1546) | delivery ngayong tag ulan (1491) | delivery ngayong tag ulan (1491) | delivery ngayong tag ulan (1491) | jollibee app at makakuha (1491) | delivery ngayong tag ulan (1491) |
| 12 | disaster risk (1546) | free jolly spaghetti (1491) | free jolly spaghetti (1491) | free jolly spaghetti (1491) | ly jollibee tag ulan (1491) | ly jollibee tag ulan (1491) |
| 13 | disaster risk reduction (1546) | jollibee app at makakuha (1491) | jollibee app at makakuha (1491) | jollibee app at makakuha (1491) | mag order ng chickenjoy (1491) | ang lks ng ulan (1321) |
| 14 | disaster risk reduction and (1546) | ly jollibee tag ulan (1491) | ly jollibee tag ulan (1491) | ly jollibee tag ulan (1491) | makakuha ng free jolly (1491) | ang lakass ng ulan (1292) |
| 15 | management council (1546) | mag order ng chickenjoy (1491) | mag order ng chickenjoy (1491) | mag order ng chickenjoy (1491) | lks ng ulan (1321) | baha na naman (1287) |

### sg

Cụm đáp án mà **2 pha** bỏ sót: the queue damn long

| # | baseline topic_global | 2 pha (từ vựng) | stoplist dùng thật + làm sạch | chỉ từ nối + làm sạch | stoplist lớn cũ + làm sạch | không stoplist + làm sạch |
|---|---|---|---|---|---|---|
| 1 | coldplay music (3818) | coldplay music (3818) | coldplay music (3818) | coldplay music (3818) | coldplay music (3818) | coldplay music of the (3818) |
| 2 | coldplay music of (3818) | music of the spheres (3818) | music of the spheres (3818) | music of the spheres (3818) | music of the spheres (3818) | national stadium (3237) |
| 3 | coldplay music of the (3818) | spheres world tour (3818) | spheres world tour (3818) | spheres world tour (3818) | spheres world tour (3818) | singapore sports hub (2376) |
| 4 | music of (3818) | national stadium (3237) | national stadium (3237) | national stadium (3237) | national stadium (3237) | kallang mrt (2338) |
| 5 | music of the (3818) | singapore sports hub (2376) | singapore sports hub (2376) | singapore sports hub (2376) | singapore sports hub (2376) | resale flat (2086) |
| 6 | music of the spheres (3818) | kallang mrt (2338) | kallang mrt (2338) | kallang mrt (2338) | kallang mrt (2338) | so shiok (2021) |
| 7 | of the (3818) | resale flat (2086) | resale flat (2086) | resale flat (2086) | resale flat (2086) | prime location public housing (1891) |
| 8 | of the spheres (3818) | so shiok (2021) | so shiok (2021) | so shiok (2021) | prime location public housing (1891) | cannot get (1881) |
| 9 | of the spheres world (3818) | prime location public housing (1891) | prime location public housing (1891) | prime location public housing (1891) | common room (1606) | a room near kallang (1606) |
| 10 | spheres world (3818) | cannot get (1881) | cannot get (1881) | cannot get (1881) | dm or check bit (1606) | common room from (1606) |
| 11 | spheres world tour (3818) | common room (1606) | common room (1606) | common room (1606) | looking for a room (1606) | dm or check bit (1606) |
| 12 | the spheres (3818) | dm or check bit (1606) | dm or check bit (1606) | dm or check bit (1606) | ly kallang room rent (1606) | ly kallang room rent (1606) |
| 13 | the spheres world (3818) | looking for a room (1606) | looking for a room (1606) | looking for a room (1606) | move in immediately (1606) | move in immediately (1606) |
| 14 | the spheres world tour (3818) | ly kallang room rent (1606) | ly kallang room rent (1606) | ly kallang room rent (1606) | no agent fee (1606) | no agent fee (1606) |
| 15 | world tour (3818) | move in immediately (1606) | move in immediately (1606) | move in immediately (1606) | room from 900 month (1606) | room from 900 month (1606) |

### th

Cụm đáp án mà **2 pha** bỏ sót: รถไฟฟ้ามหานครสายเฉลิมรัชมงคล

| # | baseline topic_global | 2 pha (từ vựng) | stoplist dùng thật + làm sạch | chỉ từ nối + làm sạch | stoplist lớn cũ + làm sạch | không stoplist + làm sạch |
|---|---|---|---|---|---|---|
| 1 | เจ ไฝ (5506) | line man (3620) | line man (3620) | line man (3620) | line man (3620) | line man (3620) |
| 2 | line man (3620) | ร้าน​เจ๊​ไฝ (2922) | ร้าน​เจ๊​ไฝ (2922) | ร้าน​เจ๊​ไฝ (2922) | ร้าน​เจ๊​ไฝ (2922) | ร้าน​เจ๊​ไฝ (2922) |
| 3 | วัน นี (3449) | มิชลิน​ไกด์ (2673) | มิชลิน​ไกด์ (2673) | มิชลิน​ไกด์ (2673) | มิชลิน​ไกด์ (2673) | มิชลิน​ไกด์ (2673) |
| 4 | มาก กก (3334) | สถานี​สยาม (2585) | สถานี​สยาม (2585) | สถานี​สยาม (2585) | สถานี​สยาม (2585) | สถานี​สยาม (2585) |
| 5 | รถไฟฟา bts (3323) | คน​เยอะ (2214) | คน​เยอะ (2214) | คน​เยอะ (2214) | คน​เยอะ (2214) | คน​เยอะ (2214) |
| 6 | ราน เจ (2940) | ต่อ​คิว​นาน (2156) | ต่อ​คิว​นาน (2156) | ต่อ​คิว​นาน (2156) | คิว​นาน (2156) | ต่อ​คิว​นาน (2156) |
| 7 | ราน เจ ไฝ (2940) | แยก​อโศก (2101) | แยก​อโศก (2101) | แยก​อโศก (2101) | แยก​อโศก (2101) | แยก​อโศก (2101) |
| 8 | ชลิน ไกด (2673) | ไป​ทำงาน​สาย​ย (1909) | ไป​ทำงาน​สาย​ย (1909) | คุ้ม​เลย (1940) | ทำงาน​สาย​ย (1909) | คุ้ม​เลย (1940) |
| 9 | สถานี สยาม (2585) | โอ้ย​ย (1764) | โอ้ย​ย (1764) | ไป​ทำงาน​สาย​ย (1909) | โอ้ย​ย (1764) | ไป​ทำงาน​สาย​ย (1909) |
| 10 | มิ ชลิน (2418) | บอก​เลย​ว่า (1713) | บอก​เลย​ว่า (1713) | โอ้ย​ย (1764) | รถไฟฟ้า​มหานคร (1657) | โอ้ย​ย (1764) |
| 11 | มิ ชลิน ไกด (2418) | รถไฟฟ้า​มหานคร (1657) | รถไฟฟ้า​มหานคร (1657) | บอก​เลย​ว่า (1713) | สาย​เฉลิม​รัช​มงคล (1657) | บอก​เลย​ว่า (1713) |
| 12 | คิว นาน (2260) | สาย​เฉลิม​รัช​มงคล (1657) | สาย​เฉลิม​รัช​มงคล (1657) | รถไฟฟ้า​มหานคร (1657) | line man วันนี้ (1644) | รถไฟฟ้า​มหานคร (1657) |
| 13 | ตอ คิว (2260) | ห้าม​พลาด (1640) | ห้าม​พลาด (1640) | สาย​เฉลิม​รัช​มงคล (1657) | ห้าม​พลาด (1640) | สาย​เฉลิม​รัช​มงคล (1657) |
| 14 | ตอ คิว นาน (2260) | ly lineman streetfood (1638) | ly lineman streetfood (1638) | ห้าม​พลาด (1640) | ly lineman streetfood (1638) | ห้าม​พลาด (1640) |
| 15 | คน เยอะ (2214) | คลิก​เลย bit (1638) | คลิก​เลย bit (1638) | ly lineman streetfood (1638) | คลิก​เลย bit (1638) | ly lineman streetfood (1638) |
