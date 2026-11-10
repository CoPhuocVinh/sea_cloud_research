# Kiểm tra cài gói vào bản sao topic_global

**Kết quả: ĐẠT**

- ✅ core load được: ['topic_global_orig', 'topic_sea_id', 'topic_sea_ms', 'topic_sea_sg', 'topic_sea_th', 'topic_sea_tl', 'topic_vi_sea', 'topic_vi_vncore'] lỗi: {}
- ✅ schema chỉ thêm ['search_text_cloud'] + ['text_cloud_sea'] + copyField search_text→search_text_cloud, không mất trường nào ([])
- nạp 5000 mention/nước từ `holdout3`: {'id': 5000, 'ms': 5000, 'th': 5000, 'tl': 5000, 'sg': 5000}
- ✅ tìm kiếm giống bản gốc (gốc, đã cài): {'search_text:bca': (1333, 1333), 'search_text:"indonesian idol"': (884, 884), 'search_text:saldo': (616, 616), 'search_text:"transfer gagal"': (201, 201), 'search_text:dana': (1793, 1793)}
- ✅ topic_sea_id: có cụm và hashtag
- ✅ topic_sea_ms: có cụm và hashtag
- ✅ topic_sea_th: có cụm và hashtag
- ✅ topic_sea_tl: có cụm và hashtag
- ✅ topic_sea_sg: có cụm và hashtag
- ✅ atomic update tính lại cụm và hashtag cho doc f7782ee4-fc9c-87b3-b26c-1190a1b62a4a

## Wordcloud theo nước (facet thô, top 8 cụm, top 3 hashtag)

| Nước | Cụm | Hashtag |
|---|---|---|
| id | indonesian idol (884), bca mobile (810), saldo sudah (616), saldo sudah kepotong (616), sudah kepotong (616), halo bca (591), bagus banget (453), suaranya bagus (453) | #indonesianidol (842), #bcamobile (836), #dana (722) |
| ms | hari raya (1075), hari raya aidilfitri (774), raya aidilfitri (774), lebuhraya utara (586), lebuhraya utara selatan (586), utara selatan (586), jem teruk (431), telekom malaysia (425) | #hariraya (819), #unifi (804), #maxis (731) |
| th | pro league (1112), rov pro (1112), rov pro league (1112), ทีมไทย (910), เล่นน้ำ (650), สุดยอดไป (615), buriram united (576), buriram united esports (576) | #rovproleague (1076), #rov (831), #สงกรานต์ (712) |
| tl | mpl ph (815), blacklist international (777), bang bang (602), mobile legends (602), dumoble yung (564), grand finals (542), mpl philippines (542), mpl philippines season (542) | #meralco (860), #mplph (812), #blacklistinternational (783) |
| sg | orchard road (1248), iphone 18 pro (1167), iphone 18 pro max (1167), pro max (1167), apple iphone (765), apple iphone 18 pro (765), apple orchard (639), apple orchard road (639) | #iphone (862), #iphone18promax (769), #orchardroad (688) |

