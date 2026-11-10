# Wordcloud trên data SEA TỔNG HỢP: baseline topic_global vs analyzer mới

Sinh bởi `scripts/compare_sea_data.py`. Data: `data/holdout` (sinh bởi `scripts/gen_sea_data.py`, seed cố định). **Không phải data thật.** Gazetteer tắt ở mọi core đánh giá.

Chấm trên top 50: hit / dup / fragment / noise (số mục), recall = số cụm đáp án (≥ 2 từ) có mặt.

| Nước | Cách | distinct | recall | hit | dup | fragment | noise |
|---|---|---|---|---|---|---|---|
| id | baseline topic_global | 185199 | 6/14 | 6 | 4 | 21 | 19 |
| id | 2 pha (từ vựng) | 496 | 12/14 | 12 | 10 | 5 | 23 |
| id | stoplist dùng thật + làm sạch | 48726 | 12/14 | 12 | 10 | 5 | 23 |
| id | chỉ từ nối + làm sạch | 48726 | 12/14 | 12 | 10 | 5 | 23 |
| id | stoplist lớn cũ + làm sạch | 13509 | 11/14 | 11 | 8 | 8 | 23 |
| id | không stoplist + làm sạch | 61605 | 12/14 | 12 | 10 | 5 | 23 |
| ms | baseline topic_global | 181832 | 6/13 | 6 | 2 | 24 | 18 |
| ms | 2 pha (từ vựng) | 463 | 12/13 | 12 | 6 | 1 | 31 |
| ms | stoplist dùng thật + làm sạch | 43340 | 12/13 | 12 | 6 | 1 | 31 |
| ms | chỉ từ nối + làm sạch | 43340 | 12/13 | 12 | 6 | 1 | 31 |
| ms | stoplist lớn cũ + làm sạch | 8942 | 12/13 | 12 | 6 | 1 | 31 |
| ms | không stoplist + làm sạch | 60744 | 12/13 | 12 | 6 | 1 | 31 |
| tl | baseline topic_global | 180212 | 6/13 | 6 | 4 | 19 | 21 |
| tl | 2 pha (từ vựng) | 455 | 12/13 | 12 | 8 | 4 | 26 |
| tl | stoplist dùng thật + làm sạch | 38716 | 12/13 | 12 | 8 | 4 | 26 |
| tl | chỉ từ nối + làm sạch | 38716 | 12/13 | 12 | 8 | 4 | 26 |
| tl | stoplist lớn cũ + làm sạch | 8444 | 11/13 | 11 | 6 | 4 | 29 |
| tl | không stoplist + làm sạch | 59464 | 12/13 | 12 | 8 | 6 | 24 |
| sg | baseline topic_global | 175862 | 4/12 | 4 | 2 | 18 | 26 |
| sg | 2 pha (từ vựng) | 450 | 12/12 | 12 | 7 | 7 | 24 |
| sg | stoplist dùng thật + làm sạch | 51092 | 12/12 | 12 | 7 | 7 | 24 |
| sg | chỉ từ nối + làm sạch | 51092 | 12/12 | 12 | 7 | 7 | 24 |
| sg | stoplist lớn cũ + làm sạch | 20625 | 10/12 | 10 | 5 | 8 | 27 |
| sg | không stoplist + làm sạch | 57917 | 12/12 | 12 | 7 | 7 | 24 |
| th | baseline topic_global | 176581 | 0/12 | 0 | 0 | 0 | 50 |
| th | 2 pha (từ vựng) | 345 | 10/12 | 10 | 2 | 3 | 35 |
| th | stoplist dùng thật + làm sạch | 41660 | 10/12 | 10 | 2 | 3 | 35 |
| th | chỉ từ nối + làm sạch | 59924 | 9/12 | 9 | 2 | 3 | 36 |
| th | stoplist lớn cũ + làm sạch | 10488 | 7/12 | 7 | 1 | 6 | 36 |
| th | không stoplist + làm sạch | 65235 | 9/12 | 9 | 2 | 3 | 36 |

## Cụm lọt vào nhờ luật nới (phủ định / từ nhấn cuối cụm)

Đo phần hại của luật nới: cụm nào trong top 50 của 2 pha chỉ có mặt nhờ luật đó, và nó là đáp án hay rác.

| Nước | Cụm (mention) trong top 50 của 2 pha | Lọt nhờ luật | Là |
|---|---|---|---|
| id | tidak enak (2539) | phủ định 'tidak' | noise |
| id | telat banget (2140) | từ cuối 'banget' | đáp án |
| id | tlt banget (734) | từ cuối 'banget' | noise |
| ms | tidak cukup (2735) | phủ định 'tidak' | noise |
| ms | tidak cukup duit (2050) | phủ định 'tidak' | noise |
| ms | mahal gila (1876) | từ cuối 'gila' | đáp án |
| ms | tidak cukup duet (747) | phủ định 'tidak' | noise |
| tl | galing talaga (2503) | từ cuối 'talaga' | đáp án |
| tl | kawawa naman (2377) | từ cuối 'naman' | fragment |
| tl | hindi pa tapos (1932) | phủ định 'hindi' | đáp án |
| tl | ayan na (1245) | từ cuối 'na' | noise |
| tl | galeng talaga (844) | từ cuối 'talaga' | đáp án |
| tl | ginebra kawawa naman (237) | từ cuối 'naman' | noise |
| tl | coco martin galing talaga (222) | từ cuối 'talaga' | noise |
| tl | ginebra galing talaga (206) | từ cuối 'talaga' | noise |
| tl | coco martin kawawa naman (169) | từ cuối 'naman' | noise |
| sg | so expensive sia (2465) | từ cuối 'sia' | đáp án |
| sg | cannot tahan (1685) | phủ định 'cannot' | đáp án |
| sg | not worth it (1208) | phủ định 'not' | đáp án |
| sg | line so expensive sia (529) | từ cuối 'sia' | noise |
| sg | centre so expensive sia (320) | từ cuối 'sia' | noise |
| sg | smrt so expensive sia (281) | từ cuối 'sia' | noise |
| th | ฟิน​มาก (2185) | từ cuối 'มาก' | đáp án |
| th | ไม่​ได้ผล (1073) | phủ định 'ไม่' | đáp án |
| th | ประธาน​นักเรียน​ฟิน​มาก (220) | từ cuối 'มาก' | noise |

## Top 15 theo nước

### id

Cụm đáp án mà **2 pha** bỏ sót: bri liga 1, gak enak

| # | baseline topic_global | 2 pha (từ vựng) | stoplist dùng thật + làm sạch | chỉ từ nối + làm sạch | stoplist lớn cũ + làm sạch | không stoplist + làm sạch |
|---|---|---|---|---|---|---|
| 1 | gratis ongkir (3035) | gratis ongkir (3035) | gratis ongkir (3035) | gratis ongkir (3035) | gratis ongkir (3035) | gratis ongkir (3035) |
| 2 | persib bandung (2988) | persib bandung (2988) | persib bandung (2988) | persib bandung (2988) | persib bandung (2988) | persib bandung (2988) |
| 3 | persija jakarta (2767) | persija jakarta (2767) | persija jakarta (2767) | persija jakarta (2767) | persija jakarta (2767) | persija jakarta (2767) |
| 4 | bri liga (2681) | bri liga (2681) | bri liga (2681) | bri liga (2681) | bri liga (2681) | bri liga (2681) |
| 5 | bri liga 1 (2681) | tidak enak (2539) | tidak enak (2539) | tidak enak (2539) | tidak enak (2539) | tidak enak (2539) |
| 6 | liga 1 (2681) | telat banget (2140) | telat banget (2140) | telat banget (2140) | telat banget (2140) | telat banget (2140) |
| 7 | promo gratis (2138) | promo gratis (2138) | promo gratis (2138) | promo gratis (2138) | promo gratis (2138) | promo gratis (2138) |
| 8 | bojan hodak (1988) | coach bojan hodak (1988) | coach bojan hodak (1988) | coach bojan hodak (1988) | coach bojan hodak (1988) | coach bojan hodak (1988) |
| 9 | coach bojan (1988) | dunia 2026 zona asia (1961) | dunia 2026 zona asia (1961) | dunia 2026 zona asia (1961) | dunia 2026 zona asia (1961) | dunia 2026 zona asia (1961) |
| 10 | coach bojan hodak (1988) | kualifikasi piala dunia (1961) | kualifikasi piala dunia (1961) | kualifikasi piala dunia (1961) | kualifikasi piala dunia (1961) | kualifikasi piala dunia (1961) |
| 11 | 2026 zona (1961) | gelora bandung lautan api (1585) | gelora bandung lautan api (1585) | gelora bandung lautan api (1585) | gelora bandung lautan api (1585) | gelora bandung lautan api (1585) |
| 12 | 2026 zona asia (1961) | diskon 50 plus gratis (1579) | diskon 50 plus gratis (1579) | diskon 50 plus gratis (1579) | diskon 50 plus gratis (1579) | di gofood dan nikmati (1579) |
| 13 | dunia 2026 (1961) | gofood dan nikmati diskon (1579) | gofood dan nikmati diskon (1579) | gofood dan nikmati diskon (1579) | gofood dan nikmati diskon (1579) | diskon 50 plus gratis (1579) |
| 14 | dunia 2026 zona (1961) | gratis ongkir khusus hari (1579) | gratis ongkir khusus hari (1579) | gratis ongkir khusus hari (1579) | gratis ongkir khusus hari (1579) | gratis ongkir khusus hari (1579) |
| 15 | dunia 2026 zona asia (1961) | pesan sekarang di gofood (1579) | pesan sekarang di gofood (1579) | pesan sekarang di gofood (1579) | pesan sekarang di gofood (1579) | promo gratis ongkir (1456) |

### ms

Cụm đáp án mà **2 pha** bỏ sót: tak cukup duit

| # | baseline topic_global | 2 pha (từ vựng) | stoplist dùng thật + làm sạch | chỉ từ nối + làm sạch | stoplist lớn cũ + làm sạch | không stoplist + làm sạch |
|---|---|---|---|---|---|---|
| 1 | harimau malaya (3354) | harimau malaya (3354) | harimau malaya (3354) | harimau malaya (3354) | harimau malaya (3354) | harimau malaya (3354) |
| 2 | anwar ibrahim (2910) | datuk seri anwar ibrahim (2910) | datuk seri anwar ibrahim (2910) | datuk seri anwar ibrahim (2910) | anwar ibrahim (2910) | datuk seri anwar ibrahim (2910) |
| 3 | datuk seri (2910) | tidak cukup (2735) | tidak cukup (2735) | tidak cukup (2735) | tidak cukup (2735) | tidak cukup (2735) |
| 4 | datuk seri anwar (2910) | johor darul ta'zim (2687) | johor darul ta'zim (2687) | johor darul ta'zim (2687) | johor darul ta'zim (2687) | johor darul ta'zim (2687) |
| 5 | datuk seri anwar ibrahim (2910) | budi madani ron95 (2524) | budi madani ron95 (2524) | budi madani ron95 (2524) | budi madani ron95 (2524) | budi madani ron95 (2524) |
| 6 | seri anwar (2910) | subsidi untuk rakyat (2401) | subsidi untuk rakyat (2401) | subsidi untuk rakyat (2401) | subsidi untuk rakyat (2401) | subsidi untuk rakyat (2401) |
| 7 | seri anwar ibrahim (2910) | harga minyak (2143) | harga minyak (2143) | harga minyak (2143) | harga minyak (2143) | harga minyak (2143) |
| 8 | darul ta'zim (2687) | tidak cukup duit (2050) | tidak cukup duit (2050) | tidak cukup duit (2050) | tidak cukup duit (2050) | tidak cukup duit (2050) |
| 9 | johor darul (2687) | pemain naturalisasi (2038) | pemain naturalisasi (2038) | pemain naturalisasi (2038) | pemain naturalisasi (2038) | pemain naturalisasi (2038) |
| 10 | johor darul ta'zim (2687) | stadium nasional bukit jalil (1984) | stadium nasional bukit jalil (1984) | stadium nasional bukit jalil (1984) | stadium nasional bukit jalil (1984) | stadium nasional bukit jalil (1984) |
| 11 | budi madani (2524) | kelayakan piala asia afc (1894) | kelayakan piala asia afc (1894) | kelayakan piala asia afc (1894) | kelayakan piala asia afc (1894) | kelayakan piala asia afc (1894) |
| 12 | budi madani ron95 (2524) | mahal gila (1876) | mahal gila (1876) | mahal gila (1876) | mahal gila (1876) | mahal gila (1876) |
| 13 | madani ron95 (2524) | info lanjut (1587) | info lanjut (1587) | info lanjut (1587) | info lanjut (1587) | dan kumpul mata mesra (1587) |
| 14 | harga minyak (2143) | ini dan kumpul mata (1587) | ini dan kumpul mata (1587) | ini dan kumpul mata (1587) | isi ron95 (1587) | info lanjut (1587) |
| 15 | minyak naik (2116) | isi ron95 di mana (1587) | isi ron95 di mana (1587) | isi ron95 di mana (1587) | kumpul mata mesra berganda (1587) | aku rasa (1330) |

### tl

Cụm đáp án mà **2 pha** bỏ sót: batang quiapo

| # | baseline topic_global | 2 pha (từ vựng) | stoplist dùng thật + làm sạch | chỉ từ nối + làm sạch | stoplist lớn cũ + làm sạch | không stoplist + làm sạch |
|---|---|---|---|---|---|---|
| 1 | batang quiapo (3056) | fpj batang quiapo (3056) | fpj batang quiapo (3056) | fpj batang quiapo (3056) | fpj batang quiapo (3056) | fpj batang quiapo (3056) |
| 2 | fpj's batang (3056) | pa tapos (2835) | pa tapos (2835) | pa tapos (2835) | coco martin (2649) | pa tapos (2835) |
| 3 | fpj's batang quiapo (3056) | coco martin (2649) | coco martin (2649) | coco martin (2649) | galing talaga (2503) | coco martin (2649) |
| 4 | pa tapos (2835) | galing talaga (2503) | galing talaga (2503) | galing talaga (2503) | san miguel beermen (2447) | galing talaga (2503) |
| 5 | coco martin (2649) | san miguel beermen (2447) | san miguel beermen (2447) | san miguel beermen (2447) | kawawa naman (2377) | ng episode (2486) |
| 6 | ng episode (2486) | kawawa naman (2377) | kawawa naman (2377) | kawawa naman (2377) | june mar fajardo (2356) | san miguel beermen (2447) |
| 7 | miguel beermen (2447) | june mar fajardo (2356) | june mar fajardo (2356) | june mar fajardo (2356) | pba season 50 philippine (2007) | kawawa naman (2377) |
| 8 | san miguel (2447) | pba season 50 philippine (2007) | pba season 50 philippine (2007) | pba season 50 philippine (2007) | philippine cup finals (2007) | june mar fajardo (2356) |
| 9 | san miguel beermen (2447) | philippine cup finals (2007) | philippine cup finals (2007) | philippine cup finals (2007) | coach tim cone (1993) | pba season 50 philippine (2007) |
| 10 | june mar (2356) | coach tim cone (1993) | coach tim cone (1993) | coach tim cone (1993) | hindi pa tapos (1932) | philippine cup finals (2007) |
| 11 | june mar fajardo (2356) | hindi pa tapos (1932) | hindi pa tapos (1932) | hindi pa tapos (1932) | ganda ng episode (1727) | coach tim cone (1993) |
| 12 | mar fajardo (2356) | sayang yung lamang (1741) | sayang yung lamang (1741) | sayang yung lamang (1741) | kawawa naman si tanggol (1626) | hindi pa tapos (1932) |
| 13 | 50 philippine (2007) | ganda ng episode (1727) | ganda ng episode (1727) | ganda ng episode (1727) | 6pm sa smart araneta (1528) | sayang yung lamang (1741) |
| 14 | 50 philippine cup (2007) | kawawa naman si tanggol (1626) | kawawa naman si tanggol (1626) | kawawa naman si tanggol (1626) | abangan ang game (1528) | ganda ng episode (1727) |
| 15 | 50 philippine cup finals (2007) | 6pm sa smart araneta (1528) | 6pm sa smart araneta (1528) | 6pm sa smart araneta (1528) | bili na ng tickets (1528) | kawawa naman si tanggol (1626) |

### sg

Cụm đáp án mà **2 pha** bỏ sót: —

| # | baseline topic_global | 2 pha (từ vựng) | stoplist dùng thật + làm sạch | chỉ từ nối + làm sạch | stoplist lớn cũ + làm sạch | không stoplist + làm sạch |
|---|---|---|---|---|---|---|
| 1 | food centre (4244) | food centre (4244) | food centre (4244) | food centre (4244) | food centre (4244) | food centre (4244) |
| 2 | east west (4142) | east west line (4142) | east west line (4142) | east west line (4142) | east west line (4142) | east west line (4142) |
| 3 | east west line (4142) | train delay (2851) | train delay (2851) | train delay (2851) | train delay (2851) | train delay (2851) |
| 4 | west line (4142) | circle line (2844) | circle line (2844) | circle line (2844) | circle line (2844) | circle line (2844) |
| 5 | train delay (2851) | so expensive sia (2465) | so expensive sia (2465) | so expensive sia (2465) | expensive sia (2465) | so expensive sia (2465) |
| 6 | circle line (2844) | maxwell food centre (2425) | maxwell food centre (2425) | maxwell food centre (2425) | maxwell food centre (2425) | maxwell food centre (2425) |
| 7 | maxwell food (2425) | bus bridging (2098) | bus bridging (2098) | bus bridging (2098) | bus bridging (2098) | stuck in (2131) |
| 8 | maxwell food centre (2425) | hawker food (2085) | hawker food (2085) | hawker food (2085) | hawker food (2085) | bus bridging (2098) |
| 9 | stuck in (2131) | chinatown complex market (1985) | chinatown complex market (1985) | chinatown complex market (1985) | chinatown complex market (1985) | hawker food (2085) |
| 10 | bus bridging (2098) | complex market and food (1985) | complex market and food (1985) | complex market and food (1985) | complex market and food (1985) | chinatown complex market and (1985) |
| 11 | hawker food (2085) | train delay again (1933) | train delay again (1933) | train delay again (1933) | cannot tahan (1685) | train delay again (1933) |
| 12 | and food (1985) | worth it (1796) | worth it (1796) | worth it (1796) | favourite hawker meals (1530) | worth it (1796) |
| 13 | and food centre (1985) | so long (1759) | so long (1759) | so long (1759) | hawker meals this weekend (1530) | so long (1759) |
| 14 | chinatown complex (1985) | cannot tahan (1685) | cannot tahan (1685) | cannot tahan (1685) | limited redemptions daily (1530) | cannot tahan (1685) |
| 15 | chinatown complex market (1985) | favourite hawker meals this (1530) | favourite hawker meals this (1530) | favourite hawker meals this (1530) | weekend with our app (1530) | download at (1530) |

### th

Cụm đáp án mà **2 pha** bỏ sót: แฟนผมเป็นประธานนักเรียน, เจมีไนน์โฟร์ท

| # | baseline topic_global | 2 pha (từ vựng) | stoplist dùng thật + làm sạch | chỉ từ nối + làm sạch | stoplist lớn cũ + làm sạch | không stoplist + làm sạch |
|---|---|---|---|---|---|---|
| 1 | ผม เปน (5872) | เป็น​ประธาน​นักเรียน (3307) | เป็น​ประธาน​นักเรียน (3307) | ผม​เป็น​ประธาน​นักเรียน (3307) | ผม​เป็น​ประธาน​นักเรียน (3307) | ผม​เป็น​ประธาน​นักเรียน (3307) |
| 2 | ผม เปน ประธาน (5872) | แฟน​ผม​เป็น​ประธาน (3307) | แฟน​ผม​เป็น​ประธาน (3307) | เจ​มี​ไนน์​โฟร์ (2867) | เจ​มี​ไนน์​โฟร์ (2867) | เจ​มี​ไนน์​โฟร์ (2867) |
| 3 | เปน ประธาน (5872) | เจ​มี​ไนน์​โฟร์ (2867) | เจ​มี​ไนน์​โฟร์ (2867) | คู่​จิ้น (2550) | ไนน์​โฟร์​ท (2602) | คู่​จิ้น (2550) |
| 4 | แฟน ผม (5872) | คู่​จิ้น (2550) | คู่​จิ้น (2550) | เพราะ​เรา​คู่​กัน (2494) | หน้า​ใส (2559) | เพราะ​เรา​คู่​กัน (2494) |
| 5 | แฟน ผม เปน (5872) | เพราะ​เรา​คู่​กัน (2494) | เพราะ​เรา​คู่​กัน (2494) | หน้า​ใส​ขึ้น (2399) | คู่​จิ้น (2550) | หน้า​ใส​ขึ้น (2399) |
| 6 | แฟน ผม เปน ประธาน (5872) | หน้า​ใส​ขึ้น (2399) | หน้า​ใส​ขึ้น (2399) | เหมาะกับ​ผิว​แพ้​ง่าย (2261) | เหมาะกับ​ผิว​แพ้​ง่าย (2261) | เหมาะกับ​ผิว​แพ้​ง่าย (2261) |
| 7 | ประธาน นักเรียน (5603) | เหมาะกับ​ผิว​แพ้​ง่าย (2261) | เหมาะกับ​ผิว​แพ้​ง่าย (2261) | คุณ​ไบร์ท​วชิร​วิ (2239) | คุณ​ไบร์ท​วชิร​วิ (2239) | คุณ​ไบร์ท​วชิร​วิ (2239) |
| 8 | ผม เปน ประธาน นักเรียน (5603) | ไบร์ท​วชิร​วิ​ชญ์ (2239) | ไบร์ท​วชิร​วิ​ชญ์ (2239) | ฟิน​มาก (2185) | ฟิน​มาก (2185) | ฟิน​มาก (2185) |
| 9 | เปน ประธาน นักเรียน (5603) | ฟิน​มาก (2185) | ฟิน​มาก (2185) | รอ​ตอน​ต่อไป (1891) | รอ​ตอน​ต่อไป (1891) | รอ​ตอน​ต่อไป (1891) |
| 10 | เจ มี (5261) | รอ​ตอน​ต่อไป (1891) | รอ​ตอน​ต่อไป (1891) | สิว​ขึ้น​เยอะ (1871) | สิว​ขึ้น​เยอะ (1871) | สิว​ขึ้น​เยอะ (1871) |
| 11 | เรา คู (4768) | สิว​ขึ้น​เยอะ (1871) | สิว​ขึ้น​เยอะ (1871) | mistine ลด 50 วันนี้ (1660) | mistine ลด 50 วันนี้ (1660) | mistine ลด 50 วันนี้ (1660) |
| 12 | คู กัน (4730) | mistine ลด 50 วันนี้ (1660) | mistine ลด 50 วันนี้ (1660) | วันนี้​วัน​เดียว​เท่านั้น (1660) | วันนี้​วัน​เดียว​เท่านั้น (1660) | วันนี้​วัน​เดียว​เท่านั้น (1660) |
| 13 | เพราะ เรา (4730) | วันนี้​วัน​เดียว​เท่านั้น (1660) | วันนี้​วัน​เดียว​เท่านั้น (1660) | สั่ง​เลย (1660) | บิ​โอ​เร (1601) | สั่ง​เลย​ที่ (1660) |
| 14 | เพราะ เรา คู (4730) | บิ​โอ​เร (1601) | บิ​โอ​เร (1601) | บิ​โอ​เร (1601) | ใคร​ดู (1506) | บิ​โอ​เร (1601) |
| 15 | เพราะ เรา คู กัน (4730) | ใคร​ดู​ยัง (1506) | ใคร​ดู​ยัง (1506) | ใคร​ดู​ยัง (1506) | ฟิน​มากๆ (1174) | ใคร​ดู​ยัง (1506) |
