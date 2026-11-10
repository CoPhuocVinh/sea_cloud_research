"""So wordcloud tiếng Việt trong môi trường thử cài gói (deploy/test, cổng 8986).

    uv run --with requests scripts/compare_deploy_vn.py

- topic_vi_vncore : configset solr_facet_research (VnCoreNLP), facet TextField search_text_cloud
- topic_vi_sea    : topic_global + gói SEA (topic.country=vi, pha 2), cùng 40k mention, facet TextField search_text_cloud
Số đo khi nạp liên tục ở quy mô 2 file đầy đủ: scripts/deploy_measure_vn.sh -> results/deploy_live.md.
Dùng lại hàm đo của compare_vn.py. Ghi results/deploy_vn.md.
"""

import json
from pathlib import Path

import compare_vn as cv

cv.SOLR = "http://localhost:8986/solr"
ROOT = Path(__file__).resolve().parent.parent
CORES = {"topic_vi_vncore": "search_text_cloud", "topic_vi_sea": "search_text_cloud"}


def main() -> None:
    perf, quality, tops = [], [], {}
    for core, field in CORES.items():
        resp, _ = cv.facet(core, field, 2000, buckets=True)
        items = cv.buckets(resp)
        load = cv.RAW / f"load_{core}.json"
        rate = json.loads(load.read_text())["docs_per_sec"] if load.exists() else ""
        fq = cv.date_filter(core)
        no_fq, with_fq = cv.latency(core, field, None), cv.latency(core, field, fq)
        perf.append({"core": core, "field": field, **cv.core_status(core), "distinct": resp["facets"]["cloud"]["numBuckets"],
                     "index doc/s": rate, "cold ms": no_fq["cold_ms"], "warm ms": no_fq["warm_median_ms"],
                     "cold ms + fq 7 ngày": with_fq["cold_ms"], "warm ms + fq": with_fq["warm_median_ms"]})
        tops[core] = [(p, n) for p, n in items if not p.startswith("#")]  # hashtag xem riêng
        quality.append({"core": core, **cv.metrics(tops[core])})
        print(perf[-1])
    report = [
        "# Tiếng Việt: solr_facet_research (VnCoreNLP) vs topic_global + gói SEA",
        "",
        "Sinh bởi `scripts/compare_deploy_vn.py` (Solr 9.10.1, cổng 8986). `topic_vi_vncore` và `topic_vi_sea` cùng 40k "
        "mention (20k đầu mỗi file `exported_data_10236707.json`, `exported_data_10236681.json`). `topic_vi_sea` bật "
        "pha 2 (từ vựng đào từ chính 40k mention). Hashtag (#…) bỏ khỏi bảng cụm.",
        "",
        "## Hiệu năng",
        "",
        cv.table(perf, list(perf[0])),
        "",
        "## Chất lượng top 100",
        "",
        cv.table(quality, ["core", "single_word_pct", "junk_pct", "fragment_pct"]),
        "",
        "## Top 40 cạnh nhau",
        "",
        cv.side_by_side({"VnCoreNLP (solr_facet_research)": tops["topic_vi_vncore"],
                         "gói SEA (pha 2)": tops["topic_vi_sea"]}, 40),
        "",
    ]
    (ROOT / "results" / "deploy_vn.md").write_text("\n".join(report), encoding="utf-8")
    print("wrote results/deploy_vn.md")


if __name__ == "__main__":
    main()
