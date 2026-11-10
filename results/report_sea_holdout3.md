# Wordcloud trên data SEA TỔNG HỢP: baseline topic_global vs analyzer mới

Sinh bởi `scripts/compare_sea_data.py`. Data: `data/holdout3` (sinh bởi `scripts/gen_sea_data.py`, seed cố định). **Không phải data thật.** Gazetteer tắt ở mọi core đánh giá.

Chấm trên top 50: hit / dup / fragment / noise (số mục), recall = số cụm đáp án (≥ 2 từ) có mặt.

| Nước | Cách | distinct | recall | hit | dup | fragment | noise |
|---|---|---|---|---|---|---|---|
| id | baseline topic_global | 185386 | 4/13 | 4 | 0 | 4 | 42 |
| id | 2 pha (từ vựng) | 418 | 13/13 | 13 | 10 | 3 | 24 |
| id | stoplist dùng thật + làm sạch | 39822 | 13/13 | 13 | 10 | 3 | 24 |
| id | chỉ từ nối + làm sạch | 39822 | 13/13 | 13 | 10 | 3 | 24 |
| id | stoplist lớn cũ + làm sạch | 3704 | 12/13 | 12 | 7 | 3 | 28 |
| id | không stoplist + làm sạch | 62378 | 13/13 | 13 | 10 | 3 | 24 |
| ms | baseline topic_global | 178672 | 3/12 | 3 | 0 | 5 | 42 |
| ms | 2 pha (từ vựng) | 661 | 12/12 | 12 | 10 | 7 | 21 |
| ms | stoplist dùng thật + làm sạch | 46773 | 12/12 | 12 | 10 | 7 | 21 |
| ms | chỉ từ nối + làm sạch | 46773 | 12/12 | 12 | 10 | 7 | 21 |
| ms | stoplist lớn cũ + làm sạch | 6565 | 11/12 | 11 | 10 | 5 | 24 |
| ms | không stoplist + làm sạch | 61266 | 12/12 | 12 | 12 | 6 | 20 |
| tl | baseline topic_global | 182273 | 5/14 | 5 | 2 | 19 | 24 |
| tl | 2 pha (từ vựng) | 750 | 11/14 | 11 | 8 | 12 | 19 |
| tl | stoplist dùng thật + làm sạch | 46560 | 11/14 | 11 | 8 | 12 | 19 |
| tl | chỉ từ nối + làm sạch | 46560 | 11/14 | 11 | 8 | 12 | 19 |
| tl | stoplist lớn cũ + làm sạch | 11217 | 10/14 | 10 | 6 | 11 | 23 |
| tl | không stoplist + làm sạch | 62295 | 13/14 | 13 | 11 | 10 | 16 |
| sg | baseline topic_global | 178993 | 6/14 | 6 | 1 | 17 | 26 |
| sg | 2 pha (từ vựng) | 609 | 14/14 | 14 | 15 | 5 | 16 |
| sg | stoplist dùng thật + làm sạch | 52730 | 14/14 | 14 | 15 | 5 | 16 |
| sg | chỉ từ nối + làm sạch | 52730 | 14/14 | 14 | 15 | 5 | 16 |
| sg | stoplist lớn cũ + làm sạch | 14513 | 12/14 | 12 | 9 | 7 | 22 |
| sg | không stoplist + làm sạch | 60015 | 14/14 | 14 | 15 | 7 | 14 |
| th | baseline topic_global | 181829 | 4/13 | 4 | 1 | 11 | 34 |
| th | 2 pha (từ vựng) | 495 | 12/13 | 12 | 7 | 6 | 25 |
| th | stoplist dùng thật + làm sạch | 35163 | 12/13 | 12 | 7 | 6 | 25 |
| th | chỉ từ nối + làm sạch | 57816 | 12/13 | 12 | 8 | 6 | 24 |
| th | stoplist lớn cũ + làm sạch | 18202 | 11/13 | 11 | 5 | 7 | 27 |
| th | không stoplist + làm sạch | 72976 | 12/13 | 12 | 8 | 6 | 24 |

## Cụm lọt vào nhờ luật nới (phủ định / từ nhấn cuối cụm)

Đo phần hại của luật nới: cụm nào trong top 50 của 2 pha chỉ có mặt nhờ luật đó, và nó là đáp án hay rác.

| Nước | Cụm (mention) trong top 50 của 2 pha | Lọt nhờ luật | Là |
|---|---|---|---|
| id | suaranya bagus banget (1652) | từ cuối 'banget' | đáp án |
| id | tidak bisa login (1431) | phủ định 'tidak' | noise |
| id | suaranya bgs banget (844) | từ cuối 'banget' | noise |
| id | tidak bs login (684) | phủ định 'tidak' | noise |
| ms | jangan risau line hilang (1651) | phủ định 'jangan' | noise |
| ms | jem teruk gila (846) | từ cuối 'gila' | đáp án |
| ms | internet sloow gila (844) | từ cuối 'gila' | noise |
| ms | inet slow gila (833) | từ cuối 'gila' | đáp án |
| ms | jam teruk gila (799) | từ cuối 'gila' | đáp án |
| tl | wag nang mag alala (1628) | phủ định 'wag' | noise |
| tl | galing talaga (1463) | từ cuối 'talaga' | fragment |
| tl | wala naman (1430) | từ cuối 'naman' | fragment |
| tl | totoo ba na (1306) | từ cuối 'na' | noise |
| tl | brown out na naman (800) | từ cuối 'naman' | đáp án |
| tl | brownout na naman (763) | từ cuối 'naman' | đáp án |
| tl | galeng talaga (751) | từ cuối 'talaga' | fragment |
| sg | not gonna lie (1260) | phủ định 'not' | noise |
| sg | so ex sia (855) | từ cuối 'sia' | đáp án |
| sg | so expensive sia (804) | từ cuối 'sia' | đáp án |
| sg | so exp sia (786) | từ cuối 'sia' | đáp án |
| sg | not worth it lah (558) | phủ định 'not' | đáp án |
| th | ไม่​ไหว (1398) | phủ định 'ไม่' | fragment |
| th | รถติด​มาก (971) | từ cuối 'มาก' | đáp án |
| th | ไม่​ไหว​ละ (677) | phủ định 'ไม่' | đáp án |
| th | ไม่​ไหว​แล้ว​ว (653) | phủ định 'ไม่' | đáp án |

## Top 15 theo nước

### id

Cụm đáp án mà **2 pha** bỏ sót: —

| # | baseline topic_global | 2 pha (từ vựng) | stoplist dùng thật + làm sạch | chỉ từ nối + làm sạch | stoplist lớn cũ + làm sạch | không stoplist + làm sạch |
|---|---|---|---|---|---|---|
| 1 | indonesian idol (3463) | indonesian idol (3463) | indonesian idol (3463) | indonesian idol (3463) | indonesian idol (3463) | indonesian idol (3463) |
| 2 | bca mobile (3299) | bca mobile (3299) | bca mobile (3299) | bca mobile (3299) | bca mobile (3299) | bca mobile (3299) |
| 3 | halo bca (2324) | saldo sudah kepotong (2485) | saldo sudah kepotong (2485) | saldo sudah kepotong (2485) | saldo sudah kepotong (2485) | saldo sudah kepotong (2485) |
| 4 | suaranya bagus (1652) | halo bca (2324) | halo bca (2324) | halo bca (2324) | halo bca (2324) | halo bca (2324) |
| 5 | 50 s.d (1623) | gangguan ya (1741) | gangguan ya (1741) | gangguan ya (1741) | suaranya bagus banget (1652) | gangguan ya (1741) |
| 6 | 50 s.d rp25.000 (1623) | suaranya bagus banget (1652) | suaranya bagus banget (1652) | suaranya bagus banget (1652) | bayar pakai dana (1623) | suaranya bagus banget (1652) |
| 7 | 50 s.d rp25.000 cek (1623) | bayar pakai dana sekarang (1623) | bayar pakai dana sekarang (1623) | bayar pakai dana sekarang (1623) | cashback 50 s (1623) | bayar pakai dana sekarang (1623) |
| 8 | bayar pakai (1623) | cek syaratnya di bit (1623) | cek syaratnya di bit (1623) | cek syaratnya di bit (1623) | cek syaratnya di bit (1623) | cek syaratnya di bit (1623) |
| 9 | bayar pakai dana (1623) | dapat cashback 50 s (1623) | dapat cashback 50 s (1623) | dapat cashback 50 s (1623) | dana sekarang dapat cashback (1623) | dapat cashback 50 s (1623) |
| 10 | bayar pakai dana sekarang (1623) | ly promo dana26 (1623) | ly promo dana26 (1623) | ly promo dana26 (1623) | ly promo dana26 (1623) | ly promo dana26 (1623) |
| 11 | bit.ly promo (1623) | otoritas jasa keuangan (1531) | otoritas jasa keuangan (1531) | otoritas jasa keuangan (1531) | otoritas jasa keuangan (1531) | otoritas jasa keuangan (1531) |
| 12 | bit.ly promo dana26 (1623) | gagal terus (1465) | gagal terus (1465) | gagal terus (1465) | gagal terus (1465) | gagal terus (1465) |
| 13 | bit.ly promo dana26 pakaidana (1623) | tidak bisa login (1431) | tidak bisa login (1431) | tidak bisa login (1431) | tidak bisa login (1431) | tidak bisa login (1431) |
| 14 | cashback 50 (1623) | tolong dong (1312) | tolong dong (1312) | tolong dong (1312) | halo kak (1261) | tolong dong (1312) |
| 15 | cashback 50 s.d (1623) | ini kenapa sih (1305) | ini kenapa sih (1305) | ini kenapa sih (1305) | td pagi (1244) | ini kenapa sih (1305) |

### ms

Cụm đáp án mà **2 pha** bỏ sót: —

| # | baseline topic_global | 2 pha (từ vựng) | stoplist dùng thật + làm sạch | chỉ từ nối + làm sạch | stoplist lớn cũ + làm sạch | không stoplist + làm sạch |
|---|---|---|---|---|---|---|
| 1 | hari raya (3768) | hari raya (4366) | hari raya (4366) | hari raya (4366) | hari raya (4366) | hari raya (4366) |
| 2 | hari raya aidilfitri (3140) | hari raya aidilfitri (3140) | hari raya aidilfitri (3140) | hari raya aidilfitri (3140) | hari raya aidilfitri (3140) | hari raya aidilfitri (3140) |
| 3 | raya aidilfitri (3140) | lebuhraya utara selatan (2385) | lebuhraya utara selatan (2385) | lebuhraya utara selatan (2385) | lebuhraya utara selatan (2385) | lebuhraya utara selatan (2385) |
| 4 | lebuhraya utara (2385) | telekom malaysia (1759) | telekom malaysia (1759) | telekom malaysia (1759) | telekom malaysia (1759) | telekom malaysia (1759) |
| 5 | lebuhraya utara selatan (2385) | jem teruk (1656) | jem teruk (1656) | jem teruk (1656) | jem teruk (1656) | jem teruk (1656) |
| 6 | utara selatan (2385) | daftar di bit (1651) | daftar di bit (1651) | daftar di bit (1651) | daftar di bit (1651) | daftar di bit (1651) |
| 7 | telekom malaysia (1759) | data tanpa had (1651) | data tanpa had (1651) | data tanpa had (1651) | jangan risau line hilang (1651) | data tanpa had (1651) |
| 8 | raya ni (1703) | jangan risau line hilang (1651) | jangan risau line hilang (1651) | jangan risau line hilang (1651) | langgan unifi air rm45 (1651) | jangan risau line hilang (1651) |
| 9 | jem teruk (1656) | langgan unifi air rm45 (1651) | langgan unifi air rm45 (1651) | langgan unifi air rm45 (1651) | ly unifi raya26 (1651) | langgan unifi air rm45 (1651) |
| 10 | air rm45 (1651) | ly unifi raya26 (1651) | ly unifi raya26 (1651) | ly unifi raya26 (1651) | raya ni jangan risau (1651) | ly unifi raya26 (1651) |
| 11 | air rm45 sebulan (1651) | tiap bulan (1539) | tiap bulan (1539) | tiap bulan (1539) | komunikasi dan multimedia malaysia (1460) | tiap bulan (1539) |
| 12 | air rm45 sebulan data (1651) | aku nak tanya (1509) | aku nak tanya (1509) | aku nak tanya (1509) | maaf zahir (1252) | aku nak tanya (1509) |
| 13 | bit.ly unifi (1651) | hari ni (1495) | hari ni (1495) | hari ni (1495) | line takde lgsg (974) | hari ni (1495) |
| 14 | bit.ly unifi raya26 (1651) | komunikasi dan multimedia malaysia (1460) | komunikasi dan multimedia malaysia (1460) | komunikasi dan multimedia malaysia (1460) | balik kampong (941) | komunikasi dan multimedia malaysia (1460) |
| 15 | bit.ly unifi raya26 unifiraya (1651) | serious la (1437) | serious la (1437) | serious la (1437) | balik kg (928) | serious la (1437) |

### tl

Cụm đáp án mà **2 pha** bỏ sót: ang mahal ng kuryente, mobile legends bang bang, ang galing talaga

| # | baseline topic_global | 2 pha (từ vựng) | stoplist dùng thật + làm sạch | chỉ từ nối + làm sạch | stoplist lớn cũ + làm sạch | không stoplist + làm sạch |
|---|---|---|---|---|---|---|
| 1 | blacklist international (3112) | blacklist international (3112) | blacklist international (3112) | blacklist international (3112) | blacklist international (3112) | blacklist international (3112) |
| 2 | mpl ph (3110) | mpl ph (3110) | mpl ph (3110) | mpl ph (3110) | mpl ph (3110) | mpl ph (3110) |
| 3 | bang bang (2549) | bang bang (2549) | bang bang (2549) | bang bang (2549) | bang bang (2549) | bang bang (2549) |
| 4 | legends bang (2549) | mobile legends (2549) | mobile legends (2549) | mobile legends (2549) | mobile legends (2549) | mobile legends (2549) |
| 5 | legends bang bang (2549) | dumoble yung (2255) | dumoble yung (2255) | dumoble yung (2255) | mpl philippines season (2097) | dumoble yung (2255) |
| 6 | mobile legends (2549) | mpl philippines season (2097) | mpl philippines season (2097) | mpl philippines season (2097) | philippines season 14 grand (2097) | mpl philippines season (2097) |
| 7 | mobile legends bang (2549) | philippines season 14 grand (2097) | philippines season 14 grand (2097) | philippines season 14 grand (2097) | energy regulatory commission (1786) | philippines season 14 grand (2097) |
| 8 | mobile legends bang bang (2549) | energy regulatory commission (1786) | energy regulatory commission (1786) | energy regulatory commission (1786) | go blacklist (1727) | ang mahal ng (1930) |
| 9 | 14 grand (2097) | go blacklist (1727) | go blacklist (1727) | go blacklist (1727) | apply sa meralco kload (1628) | ng kuryente (1916) |
| 10 | 14 grand finals (2097) | alamin dito (1628) | alamin dito (1628) | alamin dito (1628) | kontrolado ang konsumo (1628) | energy regulatory commission (1786) |
| 11 | grand finals (2097) | apply sa meralco kload (1628) | apply sa meralco kload (1628) | apply sa meralco kload (1628) | ly meralco kload (1628) | go blacklist (1727) |
| 12 | mpl philippines (2097) | kontrolado ang konsumo mo (1628) | kontrolado ang konsumo mo (1628) | kontrolado ang konsumo mo (1628) | mag alala sa taas (1628) | alala sa taas ng (1628) |
| 13 | mpl philippines season (2097) | ly meralco kload (1628) | ly meralco kload (1628) | ly meralco kload (1628) | meralco kload para kontrolado (1628) | alamin dito (1628) |
| 14 | mpl philippines season 14 (2097) | mag alala sa taas (1628) | mag alala sa taas (1628) | mag alala sa taas (1628) | taas ng singil (1628) | apply sa meralco kload (1628) |
| 15 | philippines season (2097) | meralco kload para kontrolado (1628) | meralco kload para kontrolado (1628) | meralco kload para kontrolado (1628) | wag nang mag alala (1628) | ly meralco kload (1628) |

### sg

Cụm đáp án mà **2 pha** bỏ sót: —

| # | baseline topic_global | 2 pha (từ vựng) | stoplist dùng thật + làm sạch | chỉ từ nối + làm sạch | stoplist lớn cũ + làm sạch | không stoplist + làm sạch |
|---|---|---|---|---|---|---|
| 1 | orchard road (4911) | orchard road (4911) | orchard road (4911) | orchard road (4911) | orchard road (4911) | orchard road (4911) |
| 2 | 18 pro (4646) | iphone 18 pro max (4646) | iphone 18 pro max (4646) | iphone 18 pro max (4646) | iphone 18 pro max (4646) | iphone 18 pro max (4646) |
| 3 | 18 pro max (4646) | apple iphone 18 pro (3079) | apple iphone 18 pro (3079) | apple iphone 18 pro (3079) | apple iphone 18 pro (3079) | apple iphone 18 pro (3079) |
| 4 | iphone 18 (4646) | sold out (2630) | sold out (2630) | sold out (2630) | chicha san chen (2458) | sold out (2630) |
| 5 | iphone 18 pro (4646) | chicha san chen (2458) | chicha san chen (2458) | chicha san chen (2458) | apple orchard road (2436) | chicha san chen (2458) |
| 6 | iphone 18 pro max (4646) | apple orchard road (2436) | apple orchard road (2436) | apple orchard road (2436) | die die (2375) | apple orchard road (2436) |
| 7 | pro max (4646) | die die (2375) | die die (2375) | die die (2375) | ion orchard (2137) | die die (2375) |
| 8 | apple iphone (3079) | ion orchard (2137) | ion orchard (2137) | ion orchard (2137) | damn long (2062) | ion orchard (2137) |
| 9 | apple iphone 18 (3079) | damn long (2062) | damn long (2062) | damn long (2062) | die die must try (1578) | damn long (2062) |
| 10 | apple iphone 18 pro (3079) | worth it (1634) | worth it (1634) | worth it (1634) | limited stocks (1567) | worth it (1634) |
| 11 | sold out (2630) | die die must try (1578) | die die must try (1578) | die die must try (1578) | ly iphone18 sg (1567) | die die must try (1578) |
| 12 | chicha san (2458) | get up to s (1567) | get up to s (1567) | get up to s (1567) | new iphone 18 pro (1567) | and get up to (1567) |
| 13 | chicha san chen (2458) | limited stocks (1567) | limited stocks (1567) | limited stocks (1567) | order the new iphone (1567) | limited stocks (1567) |
| 14 | san chen (2458) | ly iphone18 sg (1567) | ly iphone18 sg (1567) | ly iphone18 sg (1567) | pro max now (1567) | ly iphone18 sg (1567) |
| 15 | apple orchard (2436) | max now and get (1567) | max now and get (1567) | max now and get (1567) | s 300 trade (1567) | new iphone 18 pro (1567) |

### th

Cụm đáp án mà **2 pha** bỏ sót: เล่นน้ำสงกรานต์

| # | baseline topic_global | 2 pha (từ vựng) | stoplist dùng thật + làm sạch | chỉ từ nối + làm sạch | stoplist lớn cũ + làm sạch | không stoplist + làm sạch |
|---|---|---|---|---|---|---|
| 1 | pro league (4457) | rov pro league (4457) | rov pro league (4457) | rov pro league (4457) | rov pro league (4457) | rov pro league (4457) |
| 2 | rov pro (4457) | ทีม​ไทย (3553) | ทีม​ไทย (3553) | ทีม​ไทย (3553) | ทีม​ไทย (3553) | ทีม​ไทย (3553) |
| 3 | rov pro league (4457) | เล่น​น้ำ (2589) | เล่น​น้ำ (2589) | เล่น​น้ำ (2589) | เล่น​น้ำ (2589) | เล่น​น้ำ (2589) |
| 4 | ถนน ขาวสาร (3837) | สุดยอด​ไป (2457) | สุดยอด​ไป (2457) | สุดยอด​ไป (2457) | buriram united esports (2345) | สุดยอด​ไป (2457) |
| 5 | ทีม ไทย (3553) | buriram united esports (2345) | buriram united esports (2345) | buriram united esports (2345) | talon esports (2271) | buriram united esports (2345) |
| 6 | นํา สง (2637) | talon esports (2271) | talon esports (2271) | talon esports (2271) | ถนน​ข้าวสาร (2007) | talon esports (2271) |
| 7 | เลน นํา (2637) | ถนน​ข้าวสาร (2007) | ถนน​ข้าวสาร (2007) | ถนน​ข้าวสาร (2007) | maha songkran world water (1713) | ถนน​ข้าวสาร (2007) |
| 8 | เลน นํา สง (2637) | maha songkran world water (1713) | maha songkran world water (1713) | maha songkran world water (1713) | league รับ​ส​กิน (1523) | maha songkran world water (1713) |
| 9 | ยอด ไป (2457) | league รับ​ส​กิน (1523) | league รับ​ส​กิน (1523) | league รับ​ส​กิน (1523) | ly rov rpl26 (1523) | league รับ​ส​กิน (1523) |
| 10 | สุด ยอด (2412) | ly rov rpl26 (1523) | ly rov rpl26 (1523) | ly rov rpl26 (1523) | ทีม​ไทย​ใน​ศึก (1523) | ly rov rpl26 (1523) |
| 11 | สุด ยอด ไป (2412) | ทีม​ไทย​ใน​ศึก (1523) | ทีม​ไทย​ใน​ศึก (1523) | ทีม​ไทย​ใน​ศึก (1523) | ลงทะเบียน​เลย​ที่ bit (1523) | ลงทะเบียน​เลย​ที่ bit (1523) |
| 12 | buriram united (2345) | ร่วม​เชียร์​ทีม​ไทย (1523) | ร่วม​เชียร์​ทีม​ไทย (1523) | ร่วม​เชียร์​ทีม​ไทย (1523) | ศึก rov pro league (1523) | บอก​เลย​ว่า (1496) |
| 13 | buriram united esports (2345) | ลงทะเบียน​เลย​ที่ bit (1523) | ลงทะเบียน​เลย​ที่ bit (1523) | ลงทะเบียน​เลย​ที่ bit (1523) | ส​กิน​ฟรี​ทันที (1523) | ใคร​ไป (1483) |
| 14 | united esports (2345) | บอก​เลย​ว่า (1496) | บอก​เลย​ว่า (1496) | บอก​เลย​ว่า (1496) | เชียร์​ทีม​ไทย (1523) | ไม่​ไหว (1398) |
| 15 | talon esports (2271) | ใคร​ไป (1483) | ใคร​ไป (1483) | ใคร​ไป (1483) | ไม่​ไหว (1398) | เล่น​น้ำ​สง​กราน (1334) |
