# 49 case SEA: baseline topic_global vs text_cloud_sea

Sinh bởi `scripts/compare_sea_cases.py` trên Solr 9.10.1 (core `sea_<nước>`).
Baseline = `ICUTokenizer` + `ICUFoldingFilter` (chain tìm kiếm của topic_global) + `ShingleFilter` 2–4.

**Tổng**: baseline 861 cụm, 146 vượt dấu câu, 113 mất dấu Thái · mới 210 cụm, 0 vượt dấu câu, 0 mất dấu Thái.

| Case | Baseline: cụm / vượt câu / mất dấu Thái | Mới: cụm / vượt câu / mất dấu Thái | Cụm của analyzer mới |
|---|---|---|---|
| id/name-title | 30 / 0 / 0 | 6 / 0 / 0 | selamat untuk, selamat untuk raisa andriana, untuk raisa andriana, raisa andriana, hamish daud, indonesian television awards |
| id/name-lower | 30 / 0 / 0 | 6 / 0 / 0 | selamat untuk, selamat untuk raisa andriana, untuk raisa andriana, raisa andriana, hamish daud, indonesian television awards |
| id/name-caps | 18 / 0 / 0 | 5 / 0 / 0 | selamat untuk, selamat untuk raisa andriana, untuk raisa andriana, raisa andriana, indonesian television awards |
| id/hashtag | 15 / 0 / 0 | 2 / 0 / 0 | nonton konser, seru banget |
| id/hashtag-glued | 6 / 0 / 0 | 3 / 0 / 0 | raisa keren, raisa keren banget, keren banget |
| id/redup | 24 / 6 / 0 | 16 / 0 / 0 | anak anak, anak anak suka, anak anak suka jalan, anak suka, anak suka jalan, anak suka jalan jalan, suka jalan, suka jalan jalan, jalan jalan, jalan jalan ke mall, jalan ke mall, kupu kupu, kupu kupu juga lucu, kupu juga lucu, kupu juga lucu lucu, lucu lucu |
| id/clitic | 12 / 5 / 0 | 7 / 0 / 0 | lagunya bagus, suaranya raisa, suaranya raisa merdu, suaranya raisa merdu banget, raisa merdu, raisa merdu banget, merdu banget |
| id/slang | 24 / 15 / 0 | 9 / 0 / 0 | tidak sabar, tidak sabar nunggu, tidak sabar nunggu konsernya, sabar nunggu, sabar nunggu konsernya, nunggu konsernya, tidak sabar, tidak sabar, tidak sabar |
| id/sentence | 24 / 12 / 0 | 7 / 0 / 0 | promo shopee, promo shopee 10.10 mantap, shopee 10.10 mantap, harga murah, harga murah banget, murah banget, gratis ongkir |
| id/junk | 24 / 0 / 0 | 1 / 0 / 0 | lucu banget |
| id/brand | 21 / 5 / 0 | 8 / 0 / 0 | beli iphone, beli iphone 17 pro, iphone 17 pro, iphone 17 pro max, pro max, pro max di tokopedia, max di tokopedia, pakai gopay |
| ms/name-title | 27 / 0 / 0 | 2 / 0 / 0 | siti nurhaliza, anugerah juara lagu |
| ms/name-lower | 21 / 0 / 0 | 2 / 0 / 0 | siti nurhaliza, anugerah juara lagu |
| ms/honorific | 21 / 0 / 0 | 6 / 0 / 0 | anwar ibrahim, anwar ibrahim lawat, lawat pulau pinang, lawat pulau pinang hari, pulau pinang, pulau pinang hari |
| ms/particle | 27 / 6 / 0 | 6 / 0 / 0 | best gila, best gila lah konsert, gila lah konsert, tidak sabar, tidak sabar nak pergi, sabar nak pergi |
| ms/slang | 15 / 12 / 0 | 3 / 0 / 0 | tidak sabar, tidak sabar, tidak sabar |
| ms/rojak | 18 / 6 / 0 | 6 / 0 / 0 | makan nasi lemak, makan nasi lemak 好吃, nasi lemak, nasi lemak 好吃, nasi lemak 好吃 sangat, 好吃 sangat |
| ms/redup | 12 / 0 / 0 | 11 / 0 / 0 | budak budak, budak budak suka, budak budak suka main, budak suka, budak suka main, budak suka main main, suka main, suka main main, main main, main main kat taman, main kat taman |
| ms/hashtag | 6 / 0 / 0 | 1 / 0 / 0 | konsert power |
| ms/sentence | 18 / 10 / 0 | 5 / 0 / 0 | harga minyak, harga minyak naik, minyak naik, rakyat marah, kerajaan senyap |
| th/name | 30 / 0 / 29 | 1 / 0 / 0 | ยินดีด้วยกับลิซ่า |
| th/brand | 30 / 0 / 27 | 5 / 0 / 0 | สั่งของในช้อปปี้, ช้อปปี้กับลาซาด้า, ส่งไว, ส่งไวมาก, ไวมาก |
| th/elong | 18 / 0 / 8 | 1 / 0 / 0 | ฟินมาก |
| th/hashtag | 27 / 0 / 21 | 1 / 0 / 0 | ปังมาก |
| th/mix | 21 / 0 / 0 | 16 / 0 / 0 | รีวิว iphone17, รีวิว iphone17 pro, รีวิว iphone17 pro max, iphone17 pro, iphone17 pro max, iphone17 pro max สี, pro max, pro max สี, pro max สีสวย, max สี, max สีสวย, max สีสวยมาก, สีสวย, สีสวยมาก, สวยมาก, แบตอึด |
| th/space-boundary | 15 / 0 / 12 | 3 / 0 / 0 | ราคาถูกมาก, ส่งเร็ว, แพ็คดี |
| th/tone-fold | 6 / 0 / 6 | 0 / 0 / 0 | — |
| th/title | 12 / 0 / 10 | 6 / 0 / 0 | คุณลิซ่า, คุณลิซ่าน่ารัก, คุณลิซ่าน่ารักมาก, ลิซ่าน่ารัก, ลิซ่าน่ารักมาก, น่ารักมาก |
| tl/name-title | 27 / 0 / 0 | 4 / 0 / 0 | congrats kay sarah geronimo, sarah geronimo, matteo guidicelli, asap natin to |
| tl/name-lower | 15 / 0 / 0 | 3 / 0 / 0 | congrats kay sarah geronimo, sarah geronimo, matteo guidicelli |
| tl/taglish | 27 / 6 / 0 | 5 / 0 / 0 | nag shopping, sm mall of asia, sobrang sulit, sobrang sulit talaga, sulit talaga |
| tl/affix-redup | 18 / 6 / 0 | 4 / 0 / 0 | nagpa picture, ganda ganda, ganda ganda ng view, ganda ng view |
| tl/contraction | 15 / 6 / 0 | 3 / 0 / 0 | hindi ko alam, sa'yo na, sa'yo na lang |
| tl/particle | 18 / 6 / 0 | 4 / 0 / 0 | grabe po talaga, sobrang saya, sobrang saya naman, saya naman |
| tl/abbrev | 24 / 6 / 0 | 12 / 0 / 0 | sobrang saya, sobrang saya lang, sobrang saya lang talaga, saya lang, saya lang talaga, saya lang talaga naman, sobrang saya, sobrang saya lang, sobrang saya lang talaga, saya lang, saya lang talaga, saya lang talaga naman |
| tl/hashtag | 6 / 0 / 0 | 1 / 0 / 0 | trending na |
| tl/sentence | 18 / 10 / 0 | 2 / 0 / 0 | mahal ng bigas, grabe na |
| sg/name-title | 27 / 0 / 0 | 4 / 0 / 0 | congrats to joseph schooling, joseph schooling, team singapore, sea games |
| sg/singlish | 24 / 6 / 0 | 7 / 0 / 0 | chicken rice, chicken rice damn, chicken rice damn shiok, damn shiok, damn shiok sia, shiok sia, must try |
| sg/chinese | 21 / 0 / 0 | 4 / 0 / 0 | hawker centre, char kway teow, char kway teow 很好, 很好 吃 |
| sg/apostrophe | 24 / 6 / 0 | 7 / 0 / 0 | singapore ndp, ndp 2026 was amazing, can't wait, can't wait for next, wait for next, wait for next year, next year |
| sg/caps | 12 / 0 / 0 | 2 / 0 / 0 | must try, chicken rice |
| sg/hashtag | 6 / 0 / 0 | 0 / 0 / 0 | — |
| sg/abbrev | 9 / 6 / 0 | 1 / 0 / 0 | national day parade |
| sg/sentence | 18 / 11 / 0 | 2 / 0 / 0 | queue very long, come back |
