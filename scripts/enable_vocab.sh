#!/usr/bin/env bash
# Bật pha 2 (lọc theo từ vựng) cho 1 core trong Solr thử deploy/test (cổng 8986), đúng quy trình thật:
#   1) nạp data (mọi cụm 2–4 từ)  2) đào từ vựng từ search_text_cloud  3) gắn file từ vựng vào core
#   4) tạo lại core với property cloud.vocabulary  5) nạp lại data (giờ chỉ giữ cụm trong từ vựng)
#   ./scripts/enable_vocab.sh <core> <country> <limit mỗi file> <file.json>...
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
CORE="$1" COUNTRY="$2" LIMIT="$3"; shift 3
SOLR=http://localhost:8986/solr
CONTAINER=solr_topic_global_test
MIN_COUNT="${MIN_COUNT:-20}"
VOCAB="dict/cloud_vocab_${CORE}.txt"
UV=(uv run -q --python 3.12 --with ijson --with requests)

"${UV[@]}" scripts/load_data.py --solr $SOLR --file "$@" --limit "$LIMIT" --cores "$CORE" | tail -1
mkdir -p deploy/test/build/vocab
"${UV[@]}" scripts/mine_vocabulary.py --solr $SOLR --core "$CORE" --field search_text_cloud --min-count "$MIN_COUNT" \
  --out "deploy/test/build/vocab/cloud_vocab_${CORE}.txt"
curl -sf "$SOLR/admin/cores?action=UNLOAD&core=$CORE&deleteIndex=true&deleteDataDir=true" >/dev/null
docker cp "deploy/test/build/vocab/cloud_vocab_${CORE}.txt" "$CONTAINER:/var/solr/data/$CORE/conf/$VOCAB" >/dev/null
docker exec -u 0 $CONTAINER sh -c "chown -R solr:solr /var/solr/data/$CORE; rm -f /var/solr/data/$CORE/core.properties*"
curl -sf "$SOLR/admin/cores?action=CREATE&name=$CORE&instanceDir=$CORE&property.topic.country=$COUNTRY&property.cloud.vocabulary=$VOCAB" >/dev/null
"${UV[@]}" scripts/load_data.py --solr $SOLR --file "$@" --limit "$LIMIT" --cores "$CORE" | tail -1
