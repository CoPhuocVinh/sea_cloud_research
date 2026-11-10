#!/usr/bin/env bash
# Chạy trọn đánh giá data SEA tổng hợp: sinh data → build → nạp data_<cc> → đào từ vựng → build lại
# → nạp vocab_<cc> → chấm theo đáp án (results/report_sea_synthetic.md). Cần Solr ở docker/ đang chạy.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
COUNTRIES=(id ms th tl sg)
PER_COUNTRY="${PER_COUNTRY:-20000}"
LEXICON="${LEXICON:-scripts/sea_lexicon.json}"   # bộ đáp án; held-out: scripts/sea_lexicon_holdout.json
DATA_DIR="${DATA_DIR:-data/synthetic}"
REPORT="${REPORT:-results/report_sea_synthetic.md}"
SEED="${SEED:-20261022}"
MIN_COUNT="${MIN_COUNT:-20}"
UV=(uv run -q --python 3.12 --with ijson --with requests)

restart_solr() {
  (cd docker && docker compose restart >/dev/null)
  until curl -sf localhost:8985/solr/admin/info/system >/dev/null; do sleep 2; done
  sleep 5
}

load() {  # load <prefix>
  for c in "${COUNTRIES[@]}"; do
    "${UV[@]}" scripts/load_data.py --file "$DATA_DIR/$c.json" --limit "$PER_COUNTRY" --cores "$1_$c" | tail -1
  done
}

python3 scripts/gen_sea_data.py --per-country "$PER_COUNTRY" --lexicon "$LEXICON" --out-dir "$DATA_DIR" --seed "$SEED"
./scripts/build.sh >/dev/null && restart_solr
load data
for c in "${COUNTRIES[@]}"; do
  "${UV[@]}" scripts/mine_vocabulary.py --core "data_$c" --min-count "$MIN_COUNT" \
    --out "docker/configsets/sea_cloud/conf/dict/cloud_vocab_${c}_demo.txt"
done
./scripts/build.sh >/dev/null && restart_solr
load vocab
"${UV[@]}" scripts/compare_sea_data.py --data-dir "$DATA_DIR" --report "$REPORT"
