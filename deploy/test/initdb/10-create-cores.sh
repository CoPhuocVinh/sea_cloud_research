#!/bin/bash
# Tạo core như precreate-core (copy cả configset, gồm lib/), gắn nước qua core property topic.country.
# 8 collection: 1 bản gốc đối chứng, 5 topic SEA (1 topic = 1 collection như production), 2 topic VN để so.
# Pha 2 (từ vựng) được bật sau khi nạp data bởi scripts/enable_vocab.sh (deploy_test.sh gọi).
set -e
create() {
  local core="$1" configset="$2" country="${3:-}" dir="/var/solr/data/$1"
  [[ -d "$dir" ]] && { echo "Core $core already exists"; return; }
  [[ -d "/opt/configsets/$configset" ]] || { echo "Skip $core: configset $configset chưa build"; return; }
  cp -r "/opt/configsets/$configset/" "$dir"
  : > "$dir/core.properties"
  [[ -n "$country" ]] && echo "topic.country=$country" >> "$dir/core.properties"
  echo "Created $core ($configset, country=${country:-<none>})"
}
create topic_global_orig topic_global          # bản gốc chưa cài: schema và tìm kiếm phải như cũ
for c in id ms th tl sg; do
  create "topic_sea_$c" topic_global_sea "$c"  # đã cài gói
done
create topic_vi_sea    topic_global_sea vi     # gói mới trên 40k mention VN thật
create topic_vi_vncore vncore_baseline         # cùng 40k mention, configset solr_facet_research
