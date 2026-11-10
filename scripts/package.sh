#!/usr/bin/env bash
# Đóng gói plugin để cài vào configset khác (vd. topic_global): dist/sea-cloud-<ver>/ và .tar.gz
#   ./scripts/package.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
VERSION="$(grep -m1 -o '<version>[^<]*</version>' pom.xml | sed -E 's/<\/?version>//g')"
NAME="sea-cloud-$VERSION"
OUT="dist/$NAME"
COUNTRIES=(id ms th tl sg sea vi)   # vi: chỉ để thử analyzer mới trên data VN
CONF=docker/configsets/sea_cloud/conf

mvn -q package
python3 scripts/build_resources.py >/dev/null

rm -rf "$OUT" && mkdir -p "$OUT/lib" "$OUT/conf/lang" "$OUT/conf/dict"
cp "target/sea-cloud-analysis-$VERSION.jar" "$OUT/lib/"
for c in "${COUNTRIES[@]}"; do
  cp "$CONF/lang/cloud_stop_$c.txt" "$CONF/lang/cloud_slang_$c.txt" "$CONF/lang/cloud_tail_$c.txt" "$OUT/conf/lang/"
  cp "$CONF/dict/cloud_names_$c.txt" "$OUT/conf/dict/"
done
cp "$CONF/dict/thai_extra.txt" "$OUT/conf/dict/"
python3 scripts/export_snippets.py "$OUT/snippets" >/dev/null
cp scripts/install_into_configset.py deploy/INSTALL.md "$OUT/"

tar -czf "dist/$NAME.tar.gz" -C dist "$NAME"
echo "Gói: dist/$NAME.tar.gz ($(du -h "dist/$NAME.tar.gz" | cut -f1)), $(find "$OUT" -type f | wc -l | tr -d ' ') file"
