"""Nạp mention từ file export (JSON array) vào các core để so sánh, đo thời gian index từng core.

    uv run --with ijson --with requests scripts/load_data.py \
        --file ../exported_data_10236707.json --limit 30000 --cores vn_vncore vn_vncore_dv vn_sea
    # nhiều file vào cùng core, Solr khác cổng:
    uv run ... scripts/load_data.py --solr http://localhost:8986/solr --file a.json b.json --limit 20000 --cores x

Chỉ gửi các trường cần cho wordcloud (id, domain, search_text, created_date, platform). `search_text` được
rút về ["", phần tử số 2] để mọi core nhận cùng một văn bản: baseline copyField mọi phần tử, còn update
processor chỉ đọc phần tử số 2 (BR-27). Kết quả thời gian ghi ra results/raw/load_<core>.json.
"""

import argparse
import itertools
import json
import time
from pathlib import Path

import ijson
import requests

SOLR = "http://localhost:8985/solr"
# domain: trường bắt buộc trong schema topic gốc
FIELDS = ("id", "domain", "search_text", "created_date", "platform")
RAW = Path(__file__).resolve().parent.parent / "results" / "raw"


def read_docs(paths: list[Path], limit: int):
    """limit áp cho từng file."""
    for path in paths:
        yield from read_file(path, limit)


def read_file(path: Path, limit: int):
    with path.open("rb") as f:
        for doc in itertools.islice(ijson.items(f, "item"), limit):
            out = {k: doc[k] for k in FIELDS if k in doc}
            texts = doc.get("search_text") or []
            out["search_text"] = ["", texts[1]] if len(texts) > 1 else []
            yield out


def batches(docs, size: int):
    it = iter(docs)
    while chunk := list(itertools.islice(it, size)):
        yield chunk


def load(solr: str, core: str, docs: list[dict], batch: int) -> dict:
    url = f"{solr}/{core}/update"
    print(f"loading {len(docs)} docs into {core} ...", flush=True)
    requests.post(url, json={"delete": {"query": "*:*"}}, params={"commit": "true"}, timeout=600).raise_for_status()
    start = time.monotonic()
    for chunk in batches(docs, batch):
        r = requests.post(url, json=chunk, timeout=600)
        if r.status_code != 200:
            raise SystemExit(f"{core}: {r.status_code} {r.text[:500]}")
    requests.get(url, params={"commit": "true"}, timeout=600).raise_for_status()
    seconds = time.monotonic() - start
    return {"core": core, "docs": len(docs), "seconds": round(seconds, 1), "docs_per_sec": round(len(docs) / seconds, 1)}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--file", type=Path, nargs="+", required=True)
    p.add_argument("--limit", type=int, default=30000, help="số mention tối đa mỗi file")
    p.add_argument("--solr", default=SOLR)
    p.add_argument("--batch", type=int, default=500)
    p.add_argument("--cores", nargs="+", required=True)
    args = p.parse_args()

    docs = list(read_docs(args.file, args.limit))
    print(f"read {len(docs)} docs from {', '.join(f.name for f in args.file)}")
    RAW.mkdir(parents=True, exist_ok=True)
    for core in args.cores:
        stats = load(args.solr, core, docs, args.batch)
        print(json.dumps(stats))
        (RAW / f"load_{core}.json").write_text(json.dumps(stats), encoding="utf-8")


if __name__ == "__main__":
    main()
