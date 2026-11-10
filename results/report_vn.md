# So sánh wordcloud trên data VN (topic 10236707)

Sinh bởi `scripts/compare_vn.py`. Cả 3 core đầu nhận cùng 30k mention đầu file export; `vn_sea_full` nhận toàn bộ file.

## Hiệu năng

| core | field | docs | size_mb | distinct | index doc/s | cold ms | warm ms (median) | cold ms + fq 7 ngày | warm ms + fq |
|---|---|---|---|---|---|---|---|---|---|
| vn_vncore | search_text_cloud | 30000 | 107.9 | 33057 | 24.5 | 453 | 15 | 191 | 13 |
| vn_vncore_dv | cloud_phrases | 30000 | 115.8 | 33057 | 18.3 | 49 | 20 | 129 | 20 |
| vn_sea | cloud_phrases | 30000 | 161.9 | 1825895 | 296.5 | 722 | 517 | 1135 | 297 |
| vn_sea_full | cloud_phrases | 167408 | 839.0 | 4669322 | 347.2 | 7498 | 3082 | 4363 | 1897 |
| vn_sea_vocab | cloud_phrases | 30000 | 79.2 | 223518 | 473.0 | 113 | 85 | 158 | 97 |
| vn_sea_vocab_full | cloud_phrases | 167408 | 451.8 | 224124 | 595.7 | 700 | 235 | 419 | 185 |

`cold` = truy vấn đầu tiên sau RELOAD core (gồm un-invert nếu facet trên TextField). `warm` = trung vị 10 lần chạy lại. Mỗi truy vấn lấy top 100 cụm.

## Chất lượng top 100

| core | single_word_pct | junk_pct | fragment_pct |
|---|---|---|---|
| vn_vncore | 1.0 | 0.0 | 1.0 |
| vn_vncore_dv | 1.0 | 0.0 | 1.0 |
| vn_sea | 0.0 | 0.0 | 28.0 |
| vn_sea_vocab | 0.0 | 0.0 | 0.0 |

- `single_word_pct`: mục 1 từ (FRD muốn cụm 2–4 từ). `junk_pct`: chứa số, `=`, `/`, `.`, `_`, `@` hoặc ≤ 2 ký tự.
- `fragment_pct`: mục bị một cụm dài hơn chứa nó và phủ ≥ 80% số mention của nó.
- Trùng top 50 giữa vn_vncore và vn_sea: 23/50.

## Top 50 cạnh nhau

| # | vn_vncore | vn_vncore_dv | vn_sea (thô) | vn_sea (tỉa cụm con) |
|---|---|---|---|---|
| 1 | đại hội (16370) | đại hội (16370) | đại hội (16690) | đại hội (16690) |
| 2 | toàn quốc (11901) | toàn quốc (11901) | xiv của đảng (14049) | xiv của đảng (14049) |
| 3 | đại biểu (11783) | đại biểu (11783) | lần thứ (13081) | toàn quốc lần thứ (11469) |
| 4 | phát triển (9059) | phát triển (9059) | thứ xiv (12297) | quốc lần thứ xiv (11108) |
| 5 | đất nước (8803) | đất nước (8803) | lần thứ xiv (12283) | đại hội đại biểu (10741) |
| 6 | tổ chức (8112) | tổ chức (8112) | toàn quốc (11931) | thứ xiv của đảng (10663) |
| 7 | chính trị (8081) | chính trị (8081) | đại biểu (11797) | đại biểu toàn quốc (10543) |
| 8 | việt nam (7917) | việt nam (7917) | quốc lần (11557) | hội đại biểu toàn (10503) |
| 9 | xây dựng (7798) | xây dựng (7798) | toàn quốc lần (11552) | biểu toàn quốc lần (10405) |
| 10 | thực hiện (7507) | thực hiện (7507) | quốc lần thứ (11473) | việt nam (9620) |
| 11 | nhân dân (7349) | nhân dân (7349) | toàn quốc lần thứ (11469) | phát triển (9066) |
| 12 | quan trọng (7265) | quan trọng (7265) | quốc lần thứ xiv (11108) | đại hội xiv (9066) |
| 13 | lãnh đạo (6904) | lãnh đạo (6904) | hội đại (10761) | chính trị (8863) |
| 14 | đặc biệt (6873) | đặc biệt (6873) | đại hội đại (10748) | đất nước (8809) |
| 15 | tinh thần (6775) | tinh thần (6775) | hội đại biểu (10746) | tổ chức (8121) |
| 16 | xã hội (6647) | xã hội (6647) | đại hội đại biểu (10741) | xã hội (7870) |
| 17 | chào mừng (6506) | chào mừng (6506) | thứ xiv của đảng (10663) | xây dựng (7814) |
| 18 | dân tộc (6441) | dân tộc (6441) | biểu toàn (10547) | nhân dân (7549) |
| 19 | góp phần (6437) | góp phần (6437) | biểu toàn quốc (10547) | thực hiện (7512) |
| 20 | tiếp tục (6135) | tiếp tục (6135) | đại biểu toàn (10543) | hội xiv của đảng (7346) |
| 21 | trách nhiệm (6076) | trách nhiệm (6076) | đại biểu toàn quốc (10543) | quan trọng (7288) |
| 22 | công tác (6051) | công tác (6051) | hội đại biểu toàn (10503) | lãnh đạo (6928) |
| 23 | đồng thời (6019) | đồng thời (6019) | biểu toàn quốc lần (10405) | đặc biệt (6885) |
| 24 | mục tiêu (5903) | mục tiêu (5903) | việt nam (9620) | tinh thần (6782) |
| 25 | ý nghĩa (5700) | ý nghĩa (5700) | hội xiv (9066) | dân tộc (6555) |
| 26 | hoạt động (5433) | hoạt động (5433) | phát triển (9066) | góp phần (6440) |
| 27 | chiến lược (5432) | chiến lược (5432) | đại hội xiv (9066) | tiếp tục (6137) |
| 28 | đổi mới (5386) | đổi mới (5386) | chính trị (8863) | trách nhiệm (6083) |
| 29 | quốc gia (5381) | quốc gia (5381) | đất nước (8809) | công tác (6051) |
| 30 | cán bộ (5352) | cán bộ (5352) | tổ chức (8121) | đồng thời (6022) |
| 31 | không chỉ (5273) | không chỉ (5273) | xã hội (7870) | chào mừng đại hội (6000) |
| 32 | kỷ nguyên (5222) | kỷ nguyên (5222) | xây dựng (7814) | mục tiêu (5904) |
| 33 | kinh tế (5162) | kinh tế (5162) | nhân dân (7549) | niềm tin (5733) |
| 34 | khẳng định (5033) | khẳng định (5033) | thực hiện (7512) | ý nghĩa (5717) |
| 35 | bảo đảm (5008) | bảo đảm (5008) | hội xiv của đảng (7346) | chiến lược (5445) |
| 36 | đối với (5002) | đối với (5002) | quan trọng (7288) | hoạt động (5440) |
| 37 | thể hiện (4995) | thể hiện (4995) | lãnh đạo (6928) | quốc gia (5400) |
| 38 | nhiệm vụ (4994) | nhiệm vụ (4994) | đặc biệt (6885) | đổi mới (5388) |
| 39 | giai đoạn (4985) | giai đoạn (4985) | tinh thần (6782) | cán bộ (5357) |
| 40 | nhà nước (4975) | nhà nước (4975) | chào mừng (6557) | nâng cao (5292) |
| 41 | sự kiện (4923) | sự kiện (4923) | dân tộc (6555) | kinh tế (5289) |
| 42 | hiệu quả (4875) | hiệu quả (4875) | góp phần (6440) | kỷ nguyên (5253) |
| 43 | triển khai (4868) | triển khai (4868) | mừng đại (6170) | nhà nước (5086) |
| 44 | bảo vệ (4853) | bảo vệ (4853) | mừng đại hội (6154) | thể hiện (5047) |
| 45 | trung tâm (4797) | trung tâm (4797) | tiếp tục (6137) | khẳng định (5037) |
| 46 | an ninh (4441) | an ninh (4441) | trách nhiệm (6083) | bảo đảm (5012) |
| 47 | vai trò (4439) | vai trò (4439) | công tác (6051) | nhiệm vụ (4995) |
| 48 | nền tảng (4413) | nền tảng (4413) | đồng thời (6022) | giai đoạn (4986) |
| 49 | hệ thống (4400) | hệ thống (4400) | chào mừng đại (6004) | bảo vệ (4880) |
| 50 | mà còn (4390) | mà còn (4390) | chào mừng đại hội (6000) | hiệu quả (4880) |
