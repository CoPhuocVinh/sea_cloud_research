#!/usr/bin/env bash
# Build plugin + gom configset vào docker/build/ để docker compose mount.
#   MVN=/path/to/mvn ./scripts/build.sh
# Cần: JDK 11+, Maven (biến MVN, mặc định `mvn`), repo ../vncore_nlp_research và ../solr_facet_research,
# model POS VnCoreNLP ở docker/build/models/postagger/vi-tagger (xem scripts/fetch_vncore_model.sh).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKPLACE="$(cd "$ROOT/.." && pwd)"
MVN="${MVN:-mvn}"
BUILD="$ROOT/docker/build"
CS="$BUILD/configsets"

echo "== 1. Plugin sea-cloud-analysis"
(cd "$ROOT" && "$MVN" -q package)
PLUGIN_JAR="$ROOT/target/sea-cloud-analysis-0.1.0.jar"

echo "== 2. Plugin VnCoreNLP (build từ bản copy, không đụng target/ của repo gốc)"
VN_SRC="$BUILD/vncore-src"
rm -rf "$VN_SRC" && mkdir -p "$VN_SRC"
(cd "$WORKPLACE/vncore_nlp_research" && tar --exclude=target --exclude=.git -cf - .) | tar -xf - -C "$VN_SRC"
(cd "$VN_SRC" && "$MVN" -q package -Dmaven.test.skip=true)

rm -rf "$CS" && mkdir -p "$CS"

echo "== 3. Configset sea_cloud"
cp -R "$ROOT/docker/configsets/sea_cloud" "$CS/sea_cloud"
mkdir -p "$CS/sea_cloud/lib" && cp "$PLUGIN_JAR" "$CS/sea_cloud/lib/"

echo "== 4. Configset vncore_baseline (y nguyên solr_facet_research + file .txt bị .gitignore chặn)"
BASE="$CS/vncore_baseline"
cp -R "$WORKPLACE/solr_facet_research/wordcloud_config_solr" "$BASE"
mkdir -p "$BASE/lib"
cp "$VN_SRC"/target/solr-vn-analyzer-1.0.jar "$BASE/lib/"
# Bỏ jar Lucene 9.11 đi kèm: Solr đã có Lucene 9.12.3
find "$VN_SRC/target/lib" -name '*.jar' ! -name 'lucene-*' -exec cp {} "$BASE/lib/" \;
: > "$BASE/conf/stopwords.txt"
: > "$BASE/conf/protwords.txt"
# wdfftypes.txt rỗng làm WordDelimiterGraphFilter ném NoSuchElementException: dùng 1 dòng vô hại (ZWJ)
echo '\u200D => ALPHANUM' > "$BASE/conf/wdfftypes.txt"
# Giả định (file thật không có trong repo): không gộp cụm nào, bỏ từ đơn không phải tên riêng
echo "# trống: file gốc không có trong repo" > "$BASE/conf/cloud_phrases.txt"
echo "SINGLE" > "$BASE/conf/skip_token_types.txt"

echo "== 5. Configset vncore_dv (= baseline + update processor ghi text_cloud_vn vào docValues)"
DV="$CS/vncore_dv"
cp -R "$BASE" "$DV"
cp "$PLUGIN_JAR" "$DV/lib/"
python3 "$ROOT/scripts/patch_vncore_dv.py" "$DV/conf"

echo "== 6. Configset sea_cloud_eval (= sea_cloud + trường baseline search_text_icu) cho data tổng hợp"
cp -R "$CS/sea_cloud" "$CS/sea_cloud_eval"
python3 "$ROOT/scripts/patch_eval.py" "$CS/sea_cloud_eval/conf"

echo "Done: $CS"
