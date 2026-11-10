#!/usr/bin/env bash
# Tải model POS của VnCoreNLP (GPL-3.0, chỉ dùng để chạy baseline so sánh, không commit vào repo).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/docker/build/models/postagger"
mkdir -p "$OUT"
curl -sfL -o "$OUT/vi-tagger" https://github.com/vncorenlp/VnCoreNLP/raw/master/models/postagger/vi-tagger
echo "Saved $OUT/vi-tagger"
