# Wordcloud trên data SEA TỔNG HỢP: baseline topic_global vs analyzer mới

Sinh bởi `scripts/compare_sea_data.py`. Data: `scripts/gen_sea_data.py` (20k mention/nước, seed cố định), đáp án `data/synthetic/truth_<cc>.json`. **Không phải data thật.** Gazetteer tắt ở mọi core đánh giá.

Chấm trên top 50: hit / dup / fragment / noise (số mục), recall = số cụm đáp án (≥ 2 từ) có mặt.

| Nước | Cách | distinct | recall | hit | dup | fragment | noise |
|---|---|---|---|---|---|---|---|
| id | baseline topic_global | 182999 | 7/11 | 7 | 2 | 9 | 32 |
| id | mọi n-gram | 27699 | 11/11 | 11 | 3 | 6 | 30 |
| id | mọi n-gram + làm sạch | 27699 | 11/11 | 11 | 3 | 1 | 35 |
| id | 2 pha (từ vựng) | 307 | 11/11 | 11 | 3 | 1 | 35 |
| ms | baseline topic_global | 162804 | 9/10 | 9 | 8 | 22 | 11 |
| ms | mọi n-gram | 26630 | 10/10 | 10 | 3 | 10 | 27 |
| ms | mọi n-gram + làm sạch | 26630 | 10/10 | 10 | 2 | 1 | 37 |
| ms | 2 pha (từ vựng) | 260 | 10/10 | 10 | 2 | 1 | 37 |
| tl | baseline topic_global | 128867 | 9/10 | 9 | 3 | 16 | 22 |
| tl | mọi n-gram | 17320 | 8/10 | 8 | 0 | 8 | 34 |
| tl | mọi n-gram + làm sạch | 17320 | 8/10 | 8 | 0 | 1 | 41 |
| tl | 2 pha (từ vựng) | 320 | 8/10 | 8 | 0 | 1 | 41 |
| sg | baseline topic_global | 137858 | 9/10 | 9 | 3 | 13 | 25 |
| sg | mọi n-gram | 30006 | 10/10 | 10 | 3 | 15 | 22 |
| sg | mọi n-gram + làm sạch | 30006 | 10/10 | 10 | 2 | 0 | 38 |
| sg | 2 pha (từ vựng) | 271 | 10/10 | 10 | 2 | 0 | 38 |
| th | baseline topic_global | 88094 | 0/6 | 0 | 0 | 0 | 50 |
| th | mọi n-gram | 18352 | 6/6 | 6 | 0 | 3 | 41 |
| th | mọi n-gram + làm sạch | 18352 | 6/6 | 6 | 0 | 3 | 41 |
| th | 2 pha (từ vựng) | 822 | 6/6 | 6 | 0 | 3 | 41 |

## Top 15 theo nước

### id

Cụm đáp án mà **2 pha** bỏ sót: —

| # | baseline | mọi n-gram | + làm sạch | 2 pha |
|---|---|---|---|---|
| 1 | promo shopee (5015) | promo shopee (5015) | promo shopee gajian (5015) | promo shopee gajian (5015) |
| 2 | promo shopee gajian (5015) | promo shopee gajian (5015) | raisa andriana (3803) | raisa andriana (3803) |
| 3 | shopee gajian (5015) | shopee gajian (5015) | tidak sabar (3546) | tidak sabar (3546) |
| 4 | raisa andriana (3803) | raisa andriana (3803) | harga murah (3305) | harga murah (3305) |
| 5 | gratis ongkir (3029) | tidak sabar (3546) | keren banget (3215) | keren banget (3215) |
| 6 | anak anak (3025) | harga murah (3305) | gratis ongkir (3029) | gratis ongkir (3029) |
| 7 | indonesian idol (3023) | keren banget (3215) | jalan jalan (3029) | jalan jalan (3029) |
| 8 | in jakarta (2678) | gratis ongkir (3029) | anak anak (3025) | anak anak (3025) |
| 9 | konser raisa (2678) | jalan jalan (3029) | indonesian idol (3023) | indonesian idol (3023) |
| 10 | konser raisa live (2678) | anak anak (3025) | lucu lucu (3008) | lucu lucu (3008) |
| 11 | konser raisa live in (2678) | indonesian idol (3023) | konser raisa live (2678) | konser raisa live (2678) |
| 12 | live in (2678) | lucu lucu (3008) | raisa live in jakarta (2678) | raisa live in jakarta (2678) |
| 13 | live in jakarta (2678) | konser raisa (2678) | hamish daud (2327) | hamish daud (2327) |
| 14 | raisa live (2678) | konser raisa live (2678) | gratis ongkir seluruh indonesia (1591) | gratis ongkir seluruh indonesia (1591) |
| 15 | raisa live in (2678) | live in jakarta (2678) | promo shopee gajian diskon (1591) | promo shopee gajian diskon (1591) |

### ms

Cụm đáp án mà **2 pha** bỏ sót: —

| # | baseline | mọi n-gram | + làm sạch | 2 pha |
|---|---|---|---|---|
| 1 | siti nurhaliza (9461) | siti nurhaliza (9461) | siti nurhaliza (9461) | siti nurhaliza (9461) |
| 2 | axiata bukit (4288) | axiata bukit (4288) | konsert siti nurhaliza (4288) | konsert siti nurhaliza (4288) |
| 3 | axiata bukit jalil (4288) | axiata bukit jalil (4288) | nurhaliza di stadium axiata (4288) | nurhaliza di stadium axiata (4288) |
| 4 | bukit jalil (4288) | bukit jalil (4288) | stadium axiata bukit jalil (4288) | stadium axiata bukit jalil (4288) |
| 5 | di stadium (4288) | konsert siti (4288) | tidak sabar (4022) | tidak sabar (4022) |
| 6 | di stadium axiata (4288) | konsert siti nurhaliza (4288) | best gila (3443) | best gila (3443) |
| 7 | di stadium axiata bukit (4288) | nurhaliza di stadium (4288) | anwar ibrahim (3406) | anwar ibrahim (3406) |
| 8 | konsert siti (4288) | nurhaliza di stadium axiata (4288) | main main (3224) | main main (3224) |
| 9 | konsert siti nurhaliza (4288) | siti nurhaliza di stadium (4288) | budak budak (3180) | budak budak (3180) |
| 10 | konsert siti nurhaliza di (4288) | stadium axiata (4288) | anugerah juara lagu (3039) | anugerah juara lagu (3039) |
| 11 | nurhaliza di (4288) | stadium axiata bukit (4288) | harga minyak (3029) | harga minyak (3029) |
| 12 | nurhaliza di stadium (4288) | stadium axiata bukit jalil (4288) | rakyat marah (2471) | rakyat marah (2471) |
| 13 | nurhaliza di stadium axiata (4288) | tidak sabar (4022) | pulau pinang (2228) | pulau pinang (2228) |
| 14 | siti nurhaliza di (4288) | best gila (3443) | nasik lemak (2093) | nasik lemak (2093) |
| 15 | siti nurhaliza di stadium (4288) | anwar ibrahim (3406) | nasi lemak (2092) | nasi lemak (2092) |

### tl

Cụm đáp án mà **2 pha** bỏ sót: ang ganda, asap natin to

| # | baseline | mọi n-gram | + làm sạch | 2 pha |
|---|---|---|---|---|
| 1 | big brother (5442) | big brother (5442) | pinoy big brother gen (5442) | pinoy big brother gen (5442) |
| 2 | big brother gen (5442) | big brother gen (5442) | sarah geronimo (4651) | sarah geronimo (4651) |
| 3 | big brother gen 11 (5442) | brother gen (5442) | sobrang saya (4619) | sobrang saya (4619) |
| 4 | brother gen (5442) | pinoy big (5442) | ganda ganda (4207) | ganda ganda (4207) |
| 5 | brother gen 11 (5442) | pinoy big brother (5442) | nagpa picture (4183) | nagpa picture (4183) |
| 6 | gen 11 (5442) | pinoy big brother gen (5442) | nag shopping (4150) | nag shopping (4150) |
| 7 | pinoy big (5442) | sarah geronimo (4651) | sm mall of asia (3387) | sm mall of asia (3387) |
| 8 | pinoy big brother (5442) | sobrang saya (4619) | grabe naman (3122) | grabe naman (3122) |
| 9 | pinoy big brother gen (5442) | ganda ganda (4207) | sulit talaga (3118) | sulit talaga (3118) |
| 10 | sarah geronimo (4651) | nagpa picture (4183) | asap natin (2886) | asap natin (2886) |
| 11 | ganda ganda (4207) | nag shopping (4150) | mahal ng bigas (2679) | mahal ng bigas (2679) |
| 12 | nagpa picture (4183) | mall of asia (3387) | matteo guidicelli (2405) | matteo guidicelli (2405) |
| 13 | nag shopping (4150) | sm mall (3387) | abangan ang pinoy big (1629) | abangan ang pinoy big (1629) |
| 14 | mall of (3387) | sm mall of asia (3387) | brother gen 11 ngayong (1629) | brother gen 11 ngayong (1629) |
| 15 | mall of asia (3387) | grabe naman (3122) | vote na (1629) | vote na (1629) |

### sg

Cụm đáp án mà **2 pha** bỏ sót: —

| # | baseline | mọi n-gram | + làm sạch | 2 pha |
|---|---|---|---|---|
| 1 | grand prix (5308) | grand prix (5308) | grand prix night race (5308) | grand prix night race (5308) |
| 2 | grand prix night (5308) | grand prix night (5308) | national day parade (4710) | national day parade (4710) |
| 3 | grand prix night race (5308) | grand prix night race (5308) | chicken rice (4528) | chicken rice (4528) |
| 4 | night race (5308) | night race (5308) | must try (3980) | must try (3980) |
| 5 | prix night (5308) | prix night (5308) | joseph schooling (3310) | joseph schooling (3310) |
| 6 | prix night race (5308) | prix night race (5308) | marina bay sands (2978) | marina bay sands (2978) |
| 7 | singapore grand (5308) | singapore grand (5308) | char kway teow (2940) | char kway teow (2940) |
| 8 | singapore grand prix (5308) | singapore grand prix (5308) | changi airport (2453) | changi airport (2453) |
| 9 | singapore grand prix night (5308) | singapore grand prix night (5308) | dam shiok (1607) | dam shiok (1607) |
| 10 | day parade (4710) | day parade (4710) | limited seats (1604) | limited seats (1604) |
| 11 | national day (4710) | national day (4710) | prix night race now (1604) | prix night race now (1604) |
| 12 | national day parade (4710) | national day parade (4710) | tickets for the singapore (1604) | tickets for the singapore (1604) |
| 13 | joseph schooling (3310) | chicken rice (4528) | damn shiok (1544) | damn shiok (1544) |
| 14 | bay sands (2978) | must try (3980) | queue damn long (1359) | queue damn long (1359) |
| 15 | marina bay (2978) | joseph schooling (3310) | queue very long (1296) | queue very long (1296) |

### th

Cụm đáp án mà **2 pha** bỏ sót: —

| # | baseline | mọi n-gram | + làm sạch | 2 pha |
|---|---|---|---|---|
| 1 | ลิ ซา (9675) | ส่งไว (6161) | ส่งไว (6161) | ส่งไว (6161) |
| 2 | ชอป ปี (7345) | ฟินมาก (4811) | ฟินมาก (4811) | ฟินมาก (4811) |
| 3 | สง ไว (6161) | ราคาดี (3580) | ราคาดี (3580) | ราคาดี (3580) |
| 4 | ทุก คน (5106) | คอนเสิร์ตลิซ่า (3193) | คอนเสิร์ตลิซ่า (3193) | คอนเสิร์ตลิซ่า (3193) |
| 5 | พรุง นี (5023) | รีวิวสินค้า (3123) | รีวิวสินค้า (3123) | รีวิวสินค้า (3123) |
| 6 | วัน นี (4967) | เพลงเพราะ (3064) | เพลงเพราะ (3064) | เพลงเพราะ (3064) |
| 7 | เมือ วาน (4883) | สินค้าคุณภาพ (2935) | สินค้าคุณภาพ (2935) | สินค้าคุณภาพ (2935) |
| 8 | ลา ซาด (4860) | ส่งไวมาก (2237) | ส่งไวมาก (2237) | ส่งไวมาก (2237) |
| 9 | ซาด า (4804) | ไวมาก (2237) | ไวมาก (2237) | ไวมาก (2237) |
| 10 | ลา ซาด า (4804) | ช้อปปี้ลดราคา (1586) | ช้อปปี้ลดราคา (1586) | ช้อปปี้ลดราคา (1586) |
| 11 | นา รักๆ (4720) | ช้อปปี้ลดราคาสูงสุด (1586) | ช้อปปี้ลดราคาสูงสุด (1586) | ช้อปปี้ลดราคาสูงสุด (1586) |
| 12 | ฟิ นมา (4545) | ทั่วไทย (1586) | ทั่วไทย (1586) | ทั่วไทย (1586) |
| 13 | มาก กก (3633) | ลดราคาสูงสุด (1586) | ลดราคาสูงสุด 90 ส่ง (1586) | ลดราคาสูงสุด 90 ส่ง (1586) |
| 14 | ลก พิง (3514) | ลดราคาสูงสุด 90 ส่ง (1586) | สูงสุด 90 ส่ง (1586) | สูงสุด 90 ส่ง (1586) |
| 15 | แบ ลก (3514) | สูงสุด 90 ส่ง (1586) | สูงสุด 90 ส่งไว (1586) | สูงสุด 90 ส่งไว (1586) |
