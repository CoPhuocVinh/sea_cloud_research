#!/usr/bin/env bash
# Đo bản dùng thật (copyField + TextField search_text_cloud) trên 2 file export VN ở quy mô thật, khi mention đổ
# vào liên tục (autoSoftCommit 5 s của topic_global). Chạy sau scripts/deploy_test.sh. Core đo là core TẠM: tạo ở
# đây, xoá khi xong, để danh sách collection của môi trường thử không phình ra. Kết quả: results/raw/live_*.json.
#   ./scripts/deploy_measure_vn.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
SOLR=http://localhost:8986/solr
CONTAINER=solr_topic_global_test
FILES=(../exported_data_10236707.json ../exported_data_10236681.json)
UV=(uv run -q --python 3.12 --with ijson --with requests)
TMP_CORES=(tmp_vi_full tmp_vi_full_nowarm tmp_vi_vocab_full)

create() {  # create <core> <configset>
  docker exec $CONTAINER rm -rf "/var/solr/data/$1"
  docker cp "deploy/test/build/configsets/$2" "$CONTAINER:/var/solr/data/$1" >/dev/null
  docker exec -u 0 $CONTAINER sh -c "chown -R solr:solr /var/solr/data/$1; rm -f /var/solr/data/$1/core.properties*"
  curl -sf "$SOLR/admin/cores?action=CREATE&name=$1&instanceDir=$1&property.topic.country=vi" >/dev/null
}
cleanup() {
  for c in "${TMP_CORES[@]}"; do
    curl -s "$SOLR/admin/cores?action=UNLOAD&core=$c&deleteInstanceDir=true" >/dev/null || true
  done
}
trap cleanup EXIT

echo "== 1. Core tạm: mọi cụm có/không warming, nạp toàn bộ 2 file"
create tmp_vi_full topic_global_sea
create tmp_vi_full_nowarm topic_global_sea_nowarm
create tmp_vi_vocab_full topic_global_sea
"${UV[@]}" scripts/load_data.py --solr $SOLR --file "${FILES[@]}" --limit 1000000 --cores tmp_vi_full_nowarm | tail -1 &
"${UV[@]}" scripts/load_data.py --solr $SOLR --file "${FILES[@]}" --limit 1000000 --cores tmp_vi_full | tail -1
wait

echo "== 2. Pha 2 trên core tạm thứ 3 (đào từ vựng từ chính nó)"
./scripts/enable_vocab.sh tmp_vi_vocab_full vi 1000000 "${FILES[@]}"

echo "== 3. Đo khi đang nạp liên tục (90 s mỗi core)"
for core in "${TMP_CORES[@]}"; do
  "${UV[@]}" scripts/measure_live_facet.py --core "$core" --source ../exported_data_10236681.json --duration 90
done
