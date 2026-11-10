"""Pha 1 của thiết kế 2 pha: đào từ vựng cụm của một topic từ core đã index mọi n-gram.

    uv run --with requests scripts/mine_vocabulary.py --core vn_sea_full --min-count 20 \
        --out docker/configsets/sea_cloud/conf/dict/cloud_vocab_vi_demo.txt

Giữ cụm có >= min-count mention, rồi `phrase_vocab.clean`: bỏ cụm con bị cụm dài hơn phủ >= 80% và gộp
các cửa sổ trượt chồng nhau của cụm dài hơn 4 từ. Pha 2: core đọc file này qua `vocabulary="${cloud.vocabulary:}"`, chỉ index cụm
trong từ vựng. Bản thật chạy định kỳ theo topic (job khám phá); ở đây đào trên chính data dùng để đo
(in-sample), nên chỉ để minh hoạ số giá trị phân biệt và độ trễ facet.
"""

import argparse
from pathlib import Path

import requests

from phrase_vocab import clean

SOLR = "http://localhost:8985/solr"


def frequent_phrases(solr: str, core: str, field: str, min_count: int) -> dict[str, int]:
    body = {"query": "*:*", "limit": 0,
            "facet": {"p": {"type": "terms", "field": field, "limit": -1, "mincount": min_count}}}
    r = requests.post(f"{solr}/{core}/select", json=body, timeout=1800)
    r.raise_for_status()
    # Hashtag (#…) không thuộc từ vựng cụm: tokenizer luôn phát hashtag, không qua lọc từ vựng
    return {b["val"]: b["count"] for b in r.json()["facets"]["p"]["buckets"] if not b["val"].startswith("#")}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--core", required=True)
    p.add_argument("--min-count", type=int, default=20)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--field", default="cloud_phrases", help="bản dùng thật: search_text_cloud")
    p.add_argument("--solr", default=SOLR)
    args = p.parse_args()

    counts = frequent_phrases(args.solr, args.core, args.field, args.min_count)
    kept = clean(counts)
    header = (f"# Sinh bởi scripts/mine_vocabulary.py từ core {args.core}, min-count {args.min_count}: "
              f"{len(counts)} cụm, còn {len(kept)} sau khi tỉa cụm con và gộp cửa sổ chồng nhau\n")
    args.out.write_text(header + "\n".join(sorted(kept)) + "\n", encoding="utf-8")
    print(header.strip())


if __name__ == "__main__":
    main()
