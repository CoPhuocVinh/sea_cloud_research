"""So sánh wordcloud trên data VN giữa 3 cách (cùng 30k mention) + đo facet trên core đầy đủ.

    uv run --with requests scripts/compare_vn.py

- vn_vncore    : y nguyên solr_facet_research — facet trên TextField search_text_cloud (un-invert)
- vn_vncore_dv : cùng analyzer VnCoreNLP nhưng ghi sẵn vào StrField docValues (tách hiệu ứng lưu trữ)
- vn_sea       : analyzer mới (ICU + n-gram 2–4 + stopword biên) ghi vào docValues
- vn_sea_full  : như vn_sea, toàn bộ file export (đo độ trễ khi số mention lớn hơn)
Ghi results/report_vn.md và results/raw/facets_<core>.json.
"""

import json
import re
import statistics
import time
from pathlib import Path

import requests

from phrase_vocab import RATIO as FRAGMENT_RATIO, clean, prune_subphrases

SOLR = "http://localhost:8985/solr"
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "results" / "raw"
CORES = {
    "vn_vncore": "search_text_cloud",
    "vn_vncore_dv": "cloud_phrases",
    "vn_sea": "cloud_phrases",
    "vn_sea_full": "cloud_phrases",
    "vn_sea_vocab": "cloud_phrases",
    "vn_sea_vocab_full": "cloud_phrases",
}
FULL = {"vn_sea_full", "vn_sea_vocab_full"}  # khác số doc, chỉ đo hiệu năng
TOP = 100
WARM_RUNS = 10
JUNK = re.compile(r"[0-9=_/@.:]|^\S{1,2}$")


def facet(core: str, field: str, limit: int, fq: str | None = None, buckets: bool = False) -> tuple[dict, float]:
    body = {
        "query": "*:*",
        "limit": 0,
        "facet": {"cloud": {"type": "terms", "field": field, "limit": limit, "mincount": 1, "numBuckets": buckets}},
    }
    if fq:
        body["filter"] = [fq]
    start = time.monotonic()
    r = requests.post(f"{SOLR}/{core}/select", json=body, timeout=600)
    wall = (time.monotonic() - start) * 1000
    r.raise_for_status()
    return r.json(), wall


def core_status(core: str) -> dict:
    s = requests.get(f"{SOLR}/admin/cores", params={"action": "STATUS", "core": core, "wt": "json"}, timeout=60).json()
    index = s["status"][core]["index"]
    return {"docs": index["numDocs"], "size_mb": round(index["sizeInBytes"] / 1e6, 1)}


def latency(core: str, field: str, fq: str | None) -> dict:
    requests.get(f"{SOLR}/admin/cores", params={"action": "RELOAD", "core": core}, timeout=600).raise_for_status()
    _, cold = facet(core, field, TOP, fq)
    warm = sorted(facet(core, field, TOP, fq)[1] for _ in range(WARM_RUNS))
    return {"cold_ms": round(cold), "warm_median_ms": round(statistics.median(warm)), "warm_max_ms": round(warm[-1])}


def date_filter(core: str) -> str:
    """Lọc 7 ngày cuối của data (mô phỏng filter thời gian trên dashboard)."""
    r = requests.get(f"{SOLR}/{core}/select", params={"q": "*:*", "rows": 1, "sort": "created_date desc", "fl": "id",
                                                       "stats": "true", "stats.field": "created_date"}, timeout=60).json()
    latest = r["stats"]["stats_fields"]["created_date"]["max"]
    return f"created_date:[{latest}-7DAYS TO {latest}]"


def buckets(resp: dict) -> list[tuple[str, int]]:
    return [(b["val"], b["count"]) for b in resp["facets"].get("cloud", {}).get("buckets", [])]


def metrics(items: list[tuple[str, int]]) -> dict:
    top = items[:TOP]
    phrases = [p for p, _ in top]
    single = sum(" " not in p for p in phrases)
    junk = sum(bool(JUNK.search(p)) for p in phrases)
    pruned = set(prune_subphrases(dict(items)))
    fragments = sum(p not in pruned for p in phrases)
    return {"single_word_pct": pct(single, len(top)), "junk_pct": pct(junk, len(top)), "fragment_pct": pct(fragments, len(top))}


def pct(n: int, d: int) -> float:
    return round(100 * n / d, 1) if d else 0.0


def table(rows: list[dict], cols: list[str]) -> str:
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(str(r.get(c, "")) for c in cols) + " |" for r in rows]
    return "\n".join(out)


def side_by_side(lists: dict[str, list[tuple[str, int]]], n: int) -> str:
    names = list(lists)
    rows = []
    for i in range(n):
        row = {"#": i + 1}
        for name in names:
            items = lists[name]
            row[name] = f"{items[i][0]} ({items[i][1]})" if i < len(items) else ""
        rows.append(row)
    return table(rows, ["#"] + names)


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    perf_rows, quality_rows, tops = [], [], {}
    for core, field in CORES.items():
        status = core_status(core)
        resp, _ = facet(core, field, 500, buckets=True)
        items = buckets(resp)
        (RAW / f"facets_{core}.json").write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
        load = RAW / f"load_{core}.json"
        index_rate = json.loads(load.read_text())["docs_per_sec"] if load.exists() else ""
        fq = date_filter(core)
        no_fq, with_fq = latency(core, field, None), latency(core, field, fq)
        perf_rows.append({"core": core, "field": field, **status, "distinct": resp["facets"]["cloud"].get("numBuckets"),
                          "index doc/s": index_rate,
                          "cold ms": no_fq["cold_ms"], "warm ms (median)": no_fq["warm_median_ms"],
                          "cold ms + fq 7 ngày": with_fq["cold_ms"], "warm ms + fq": with_fq["warm_median_ms"]})
        if core not in FULL:
            tops[core] = items
            quality_rows.append({"core": core, **metrics(items)})
        print(perf_rows[-1])

    base = [p for p, _ in tops["vn_vncore"][:50]]
    sea = [p for p, _ in tops["vn_sea"][:50]]
    sea_pruned = sorted(clean(dict(tops["vn_sea"])).items(), key=lambda kv: -kv[1])
    report = [
        "# So sánh wordcloud trên data VN (topic 10236707)",
        "",
        "Sinh bởi `scripts/compare_vn.py`. Cả 3 core đầu nhận cùng 30k mention đầu file export; `vn_sea_full` nhận toàn bộ file.",
        "",
        "## Hiệu năng",
        "",
        table(perf_rows, list(perf_rows[0])),
        "",
        "`cold` = truy vấn đầu tiên sau RELOAD core (gồm un-invert nếu facet trên TextField). `warm` = trung vị "
        f"{WARM_RUNS} lần chạy lại. Mỗi truy vấn lấy top {TOP} cụm.",
        "",
        "## Chất lượng top 100",
        "",
        table(quality_rows, ["core", "single_word_pct", "junk_pct", "fragment_pct"]),
        "",
        "- `single_word_pct`: mục 1 từ (FRD muốn cụm 2–4 từ). `junk_pct`: chứa số, `=`, `/`, `.`, `_`, `@` hoặc ≤ 2 ký tự.",
        f"- `fragment_pct`: mục bị một cụm dài hơn chứa nó và phủ ≥ {int(FRAGMENT_RATIO * 100)}% số mention của nó.",
        f"- Trùng top 50 giữa vn_vncore và vn_sea: {len(set(base) & set(sea))}/50.",
        "",
        "## Top 50 cạnh nhau",
        "",
        side_by_side({"vn_vncore": tops["vn_vncore"], "vn_vncore_dv": tops["vn_vncore_dv"],
                      "vn_sea (thô)": tops["vn_sea"], "vn_sea (tỉa + gộp chồng nhau)": sea_pruned}, 50),
        "",
    ]
    (ROOT / "results" / "report_vn.md").write_text("\n".join(report), encoding="utf-8")
    print("wrote results/report_vn.md")


if __name__ == "__main__":
    main()
