"""Đo facet wordcloud khi mention đổ vào liên tục (giống production: topic_global autoSoftCommit 5 giây).

    uv run --with ijson --with requests scripts/measure_live_facet.py --core tmp_vi_vocab_full \\
        --source ../exported_data_10236681.json --duration 90

- Luồng ghi: mỗi --interval giây gửi --batch mention (id mới) KHÔNG commit, để autoSoftCommit của core mở searcher mới.
- Luồng đọc: mỗi giây 1 truy vấn json.facet top 100 trên --field, ghi độ trễ.
- Độ tươi: mỗi lô có 1 mention đánh dấu; đo thời gian tới khi nó tìm thấy được.
In p50/p95/max độ trễ và độ tươi, ghi thêm 1 dòng JSON vào results/raw/live_<core>.json.
"""

import argparse
import itertools
import json
import statistics
import threading
import time
import uuid
from pathlib import Path

import ijson
import requests

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "results" / "raw"


def texts(source: Path, skip: int, n: int) -> list[dict]:
    with source.open("rb") as f:
        out = []
        for d in itertools.islice(ijson.items(f, "item"), skip, skip + n):
            st = d.get("search_text") or []
            if len(st) > 1:
                out.append({"domain": d.get("domain", "facebook.com"), "search_text": ["", st[1]],
                            "created_date": d.get("created_date"), "platform": d.get("platform", 1)})
        return out


def percentile(values: list[float], p: float) -> float:
    if not values:
        return float("nan")
    values = sorted(values)
    return values[min(len(values) - 1, int(round(p * (len(values) - 1))))]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--solr", default="http://localhost:8986/solr")
    ap.add_argument("--core", required=True)
    ap.add_argument("--field", default="search_text_cloud")
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--duration", type=int, default=90)
    ap.add_argument("--batch", type=int, default=50)
    ap.add_argument("--interval", type=float, default=2.0)
    args = ap.parse_args()

    pool = texts(args.source, 200_000, 20_000)
    stop = time.monotonic() + args.duration
    latencies, freshness, errors = [], [], []
    body = {"query": "*:*", "limit": 0, "facet": {"c": {"type": "terms", "field": args.field, "limit": 100}}}

    def writer() -> None:
        docs = itertools.cycle(pool)
        while time.monotonic() < stop:
            batch = [{**next(docs), "id": str(uuid.uuid4())} for _ in range(args.batch)]
            marker = batch[0]["id"]
            sent = time.monotonic()
            r = requests.post(f"{args.solr}/{args.core}/update", json=batch, timeout=120)
            if r.status_code != 200:
                errors.append(r.text[:200])
            threading.Thread(target=watch, args=(marker, sent), daemon=True).start()
            time.sleep(args.interval)

    def watch(marker: str, sent: float) -> None:
        while time.monotonic() < stop + 60:
            r = requests.get(f"{args.solr}/{args.core}/select", params={"q": f'id:"{marker}"', "rows": 0}, timeout=60)
            if r.ok and r.json()["response"]["numFound"]:
                freshness.append(time.monotonic() - sent)
                return
            time.sleep(0.5)

    def reader() -> None:
        while time.monotonic() < stop:
            t = time.monotonic()
            r = requests.post(f"{args.solr}/{args.core}/select", json=body, timeout=600)
            latencies.append((time.monotonic() - t) * 1000)
            if r.status_code != 200:
                errors.append(r.text[:200])
            time.sleep(max(0.0, 1 - (time.monotonic() - t)))

    threads = [threading.Thread(target=writer), threading.Thread(target=reader)]
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    time.sleep(5)
    result = {"core": args.core, "queries": len(latencies),
              "facet_p50_ms": round(statistics.median(latencies)) if latencies else None,
              "facet_p95_ms": round(percentile(latencies, 0.95)), "facet_max_ms": round(max(latencies, default=0)),
              "fresh_p50_s": round(statistics.median(freshness), 1) if freshness else None,
              "fresh_max_s": round(max(freshness), 1) if freshness else None,
              "batches_seen": len(freshness), "errors": len(errors), "first_error": errors[0] if errors else ""}
    RAW.mkdir(parents=True, exist_ok=True)
    (RAW / f"live_{args.core}.json").write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
