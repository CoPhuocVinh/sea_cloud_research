#!/usr/bin/env bash
# Thử trọn quy trình export → import vào bản sao configset topic_global → chạy Solr → kiểm tra.
#   ./scripts/deploy_test.sh            # cần Docker, Maven, ../solr-schemas/topic_global
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
TOPIC_GLOBAL="$ROOT/../solr-schemas/topic_global"
BUILD=deploy/test/build/configsets
PKG=dist/sea-cloud-$(grep -m1 -o '<version>[^<]*</version>' pom.xml | sed -E 's/<\/?version>//g')

echo "== 1. Export: đóng gói"
./scripts/package.sh

echo "== 2. Import: cài gói vào bản sao topic_global (bản gốc solr-schemas giữ nguyên)"
rm -rf "$BUILD" && mkdir -p "$BUILD/topic_global/conf"
cp -R "$TOPIC_GLOBAL/." "$BUILD/topic_global/conf/"       # solr-schemas để file phẳng; core cần conf/
cp -R "$BUILD/topic_global" "$BUILD/topic_global_sea"
cp -R "$BUILD/topic_global" "$BUILD/topic_global_sea_nowarm"
rm -rf deploy/test/build/pkg && mkdir -p deploy/test/build/pkg
tar -xzf "$PKG.tar.gz" -C deploy/test/build/pkg
INSTALLER="deploy/test/build/pkg/$(basename "$PKG")/install_into_configset.py"
python3 "$INSTALLER" "$BUILD/topic_global_sea" --with-lib --warm
echo "-- chạy lại lần 2 (phải không đổi gì ngoài copy tài nguyên/jar):"
python3 "$INSTALLER" "$BUILD/topic_global_sea" --with-lib --warm
echo "-- bản đối chứng không warming:"
python3 "$INSTALLER" "$BUILD/topic_global_sea_nowarm" --with-lib
echo "-- core đối chứng tiếng Việt: configset solr_facet_research (build bởi scripts/build.sh)"
[[ -d docker/build/configsets/vncore_baseline ]] || ./scripts/build.sh >/dev/null
[[ -f docker/build/models/postagger/vi-tagger ]] || ./scripts/fetch_vncore_model.sh
cp -R docker/build/configsets/vncore_baseline "$BUILD/vncore_baseline"

echo "== 3. Chạy Solr (cổng 8986) với core gốc + core đã cài"
(cd deploy/test && docker compose down -v >/dev/null 2>&1 || true; docker compose up -d >/dev/null)
until curl -sf localhost:8986/solr/admin/info/system >/dev/null; do sleep 2; done
sleep 8

echo "== 4. Kiểm tra"
[[ -f data/holdout3/id.json ]] || python3 scripts/gen_sea_data.py --lexicon scripts/sea_lexicon_holdout3.json \
  --out-dir data/holdout3 --seed 13
uv run -q --python 3.12 --with ijson --with requests scripts/verify_deploy.py --data-dir data/holdout3

echo "== 5. Nạp data + bật pha 2 (từ vựng theo topic) cho từng collection"
for c in id ms th tl sg; do
  ./scripts/enable_vocab.sh "topic_sea_$c" "$c" 20000 "data/holdout3/$c.json"
done
VN=(../exported_data_10236707.json ../exported_data_10236681.json)
./scripts/enable_vocab.sh topic_vi_sea vi 20000 "${VN[@]}"
uv run -q --python 3.12 --with ijson --with requests scripts/load_data.py --solr http://localhost:8986/solr \
  --file "${VN[@]}" --limit 20000 --cores topic_vi_vncore | tail -1
