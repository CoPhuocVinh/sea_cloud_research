# Tiếng Việt: solr_facet_research (VnCoreNLP) vs topic_global + gói SEA

Sinh bởi `scripts/compare_deploy_vn.py` (Solr 9.10.1, cổng 8986). `topic_vi_vncore` và `topic_vi_sea` cùng 40k mention (20k đầu mỗi file `exported_data_10236707.json`, `exported_data_10236681.json`). `topic_vi_sea` bật pha 2 (từ vựng đào từ chính 40k mention). Hashtag (#…) bỏ khỏi bảng cụm.

## Hiệu năng

| core | field | docs | size_mb | distinct | index doc/s | cold ms | warm ms | cold ms + fq 7 ngày | warm ms + fq |
|---|---|---|---|---|---|---|---|---|---|
| topic_vi_vncore | search_text_cloud | 40000 | 75.6 | 30368 | 57.0 | 98 | 7 | 188 | 13 |
| topic_vi_sea | search_text_cloud | 40000 | 73.2 | 27480 | 821.1 | 249 | 6 | 304 | 17 |

## Chất lượng top 100

| core | single_word_pct | junk_pct | fragment_pct |
|---|---|---|---|
| topic_vi_vncore | 1.0 | 0.0 | 1.0 |
| topic_vi_sea | 0.0 | 0.0 | 0.0 |

## Top 40 cạnh nhau

| # | VnCoreNLP (solr_facet_research) | gói SEA (pha 2) |
|---|---|---|
| 1 | đại hội (10862) | đại hội (11076) |
| 2 | toàn quốc (7994) | xiv của đảng (9327) |
| 3 | đại biểu (7813) | toàn quốc lần thứ (7607) |
| 4 | phát triển (6434) | thứ xiv của đảng (7073) |
| 5 | đất nước (5853) | việt nam (6455) |
| 6 | tổ chức (5348) | phát triển (6439) |
| 7 | chính trị (5337) | đại hội xiv (5981) |
| 8 | việt nam (5327) | đất nước (5858) |
| 9 | xây dựng (5150) | chính trị (5834) |
| 10 | thực hiện (4952) | tổ chức (5353) |
| 11 | quan trọng (4859) | xã hội (5173) |
| 12 | nhân dân (4783) | xây dựng (5160) |
| 13 | đặc biệt (4739) | thực hiện (4956) |
| 14 | tinh thần (4519) | nhân dân (4920) |
| 15 | lãnh đạo (4510) | quan trọng (4874) |
| 16 | xã hội (4369) | hội xiv của đảng (4864) |
| 17 | chào mừng (4354) | đặc biệt (4749) |
| 18 | dân tộc (4308) | tinh thần (4525) |
| 19 | góp phần (4249) | lãnh đạo (4524) |
| 20 | tiếp tục (4069) | góp phần (4250) |
| 21 | trách nhiệm (4028) | tiếp tục (4071) |
| 22 | công tác (3983) | trách nhiệm (4033) |
| 23 | đồng thời (3928) | chào mừng đại hội (4003) |
| 24 | mục tiêu (3859) | công tác (3983) |
| 25 | ý nghĩa (3797) | đồng thời (3931) |
| 26 | hoạt động (3611) | mục tiêu (3859) |
| 27 | chiến lược (3582) | niềm tin (3815) |
| 28 | không chỉ (3556) | ý nghĩa (3808) |
| 29 | đổi mới (3551) | hoạt động (3613) |
| 30 | quốc gia (3533) | chiến lược (3592) |
| 31 | cán bộ (3480) | đổi mới (3552) |
| 32 | kỷ nguyên (3465) | quốc gia (3546) |
| 33 | kinh tế (3403) | kinh tế (3492) |
| 34 | giai đoạn (3339) | kỷ nguyên (3484) |
| 35 | khẳng định (3325) | cán bộ (3481) |
| 36 | sự kiện (3325) | nâng cao (3454) |
| 37 | nhiệm vụ (3303) | giai đoạn (3342) |
| 38 | bảo vệ (3300) | khẳng định (3326) |
| 39 | đối với (3292) | bảo vệ (3317) |
| 40 | bảo đảm (3272) | thể hiện (3317) |
