#!/bin/bash
# Chạy mỗi lần container start (run-initdb). Tạo core từ configset nếu chưa có và gắn nước
# qua core property topic.country (schema đọc bằng ${topic.country:sea}). Core đã có thì chép lại
# conf/ và lib/ (giữ data/ và core.properties) để luôn chạy đúng bản build mới nhất.
set -e

create() {
  local core="$1" configset="$2" country="${3:-}" extra="${4:-}"
  local dir="/var/solr/data/$core"
  if [[ -d "$dir" ]]; then
    rm -rf "$dir/conf" "$dir/lib"
    cp -r "/opt/configsets/$configset/conf" "/opt/configsets/$configset/lib" "$dir/"
    echo "Refreshed $core ($configset)"
    return
  fi
  cp -r "/opt/configsets/$configset/" "$dir"
  : > "$dir/core.properties"
  [[ -n "$country" ]] && echo "topic.country=$country" >> "$dir/core.properties"
  [[ -n "$extra" ]] && echo "$extra" >> "$dir/core.properties"
  echo "Created $core ($configset, country=${country:-<none>})"
}

# So sánh trên data VN
create vn_vncore    vncore_baseline
create vn_vncore_dv vncore_dv
create vn_sea       sea_cloud vi
create vn_sea_full  sea_cloud vi   # toàn bộ file export, đo facet ở quy mô lớn
# Thiết kế 2 pha: chỉ index cụm có trong từ vựng đã đào (scripts/mine_vocabulary.py)
create vn_sea_vocab      sea_cloud vi cloud.vocabulary=dict/cloud_vocab_vi_demo.txt
create vn_sea_vocab_full sea_cloud vi cloud.vocabulary=dict/cloud_vocab_vi_demo.txt

# Mỗi nước SEA 1 core (cùng configset), cộng 1 core không khai báo nước (bộ dự phòng "sea")
for c in id ms th tl sg; do
  create "sea_$c" sea_cloud "$c"
done
create sea_default sea_cloud

# Data tổng hợp (scripts/gen_sea_data.py): data_<cc> facet được cả baseline lẫn mọi n-gram;
# vocab_<cc> chỉ index cụm trong từ vựng đã đào từ data_<cc> (scripts/mine_vocabulary.py). Cả hai tắt gazetteer.
for c in id ms th tl sg; do
  create "data_$c"  sea_cloud_eval "$c"
  create "vocab_$c" sea_cloud_eval "$c" "cloud.vocabulary=dict/cloud_vocab_${c}_demo.txt"
done
