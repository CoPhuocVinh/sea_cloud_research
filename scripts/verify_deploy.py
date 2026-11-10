"""Kiểm tra bản topic_global đã cài gói (deploy/test, Solr ở cổng 8986).

    uv run --with ijson --with requests scripts/verify_deploy.py --data-dir data/holdout3

1. mọi core load được;
2. schema bản đã cài = bản gốc + đúng các mục của gói (không mất gì);
3. tìm kiếm search_text cho kết quả giống hệt bản gốc trên cùng data;
4. wordcloud (search_text_cloud: cụm + hashtag "#…") có giá trị cho cả 5 nước;
5. atomic update ({"set": ...}) tính lại cụm (copyField chạy lại vì search_text được stored).
Ghi results/deploy_test.md.
"""

import argparse
import itertools
import sys
from pathlib import Path

import ijson
import requests

SOLR = "http://localhost:8986/solr"
ROOT = Path(__file__).resolve().parent.parent
COUNTRIES = ["id", "ms", "th", "tl", "sg"]
ORIG = "topic_global_orig"
PER_CORE = 5000
ADDED_FIELDS = {"search_text_cloud"}
FIELD = "search_text_cloud"
ADDED_TYPES = {"text_cloud_sea"}


def get(path: str, **params) -> dict:
    r = requests.get(f"{SOLR}/{path}", params={"wt": "json", **params}, timeout=120)
    r.raise_for_status()
    return r.json()


def post(core: str, body, **params) -> None:
    r = requests.post(f"{SOLR}/{core}/update", json=body, params=params, timeout=600)
    if r.status_code != 200:
        raise SystemExit(f"{core}: {r.status_code} {r.text[:400]}")


def load(core: str, file: Path) -> int:
    with file.open("rb") as f:
        docs = [{k: d[k] for k in ("id", "domain", "search_text", "created_date", "platform") if k in d}
                for d in itertools.islice(ijson.items(f, "item"), PER_CORE)]
    post(core, {"delete": {"query": "*:*"}}, commit="true")
    post(core, docs, commit="true")
    return len(docs)


def names(core: str, kind: str) -> set[str]:
    key = "fields" if kind == "fields" else "fieldTypes"
    return {f["name"] for f in get(f"{core}/schema/{kind}")[key]}


def facet(core: str, field: str, limit: int, prefix: str | None = None) -> list[tuple[str, int]]:
    terms = {"type": "terms", "field": field, "limit": limit, **({"prefix": prefix} if prefix else {})}
    body = {"query": "*:*", "limit": 0, "facet": {"f": terms}}
    r = requests.post(f"{SOLR}/{core}/select", json=body, timeout=120).json()
    return [(b["val"].replace("​", ""), b["count"]) for b in r["facets"]["f"]["buckets"]]


def count(core: str, q: str, *fqs: str) -> int:
    return get(f"{core}/select", q=q, fq=list(fqs), rows=0)["response"]["numFound"]


def term(value: str) -> str:
    """Lọc đúng 1 giá trị wordcloud: {!term} không chạy analyzer lên giá trị (TextField sẽ tách lại thành cụm)."""
    return f"{{!term f={FIELD}}}{value}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=Path, default=ROOT / "data" / "holdout3")
    args = ap.parse_args()
    report, failures = ["# Kiểm tra cài gói vào bản sao topic_global", ""], []

    def check(ok: bool, msg: str) -> None:
        report.append(f"- {'✅' if ok else '❌'} {msg}")
        if not ok:
            failures.append(msg)

    status = get("admin/cores", action="STATUS")
    check(not status.get("initFailures"), f"core load được: {sorted(status['status'])} lỗi: {status.get('initFailures')}")

    sea = "topic_sea_id"
    extra_fields = names(sea, "fields") - names(ORIG, "fields")
    missing_fields = names(ORIG, "fields") - names(sea, "fields")
    extra_types = names(sea, "fieldtypes") - names(ORIG, "fieldtypes")
    copies = {(c["source"], c["dest"]) for c in get(f"{sea}/schema/copyfields")["copyFields"]}
    copies_orig = {(c["source"], c["dest"]) for c in get(f"{ORIG}/schema/copyfields")["copyFields"]}
    check(extra_fields == ADDED_FIELDS and not missing_fields and extra_types == ADDED_TYPES
          and copies - copies_orig == {("search_text", FIELD)},
          f"schema chỉ thêm {sorted(extra_fields)} + {sorted(extra_types)} + copyField search_text→{FIELD}, "
          f"không mất trường nào ({sorted(missing_fields)})")

    loaded = {c: load(f"topic_sea_{c}", args.data_dir / f"{c}.json") for c in COUNTRIES}
    load(ORIG, args.data_dir / "id.json")
    report.append(f"- nạp {PER_CORE} mention/nước từ `{args.data_dir.name}`: {loaded}")
    queries = ["search_text:bca", 'search_text:"indonesian idol"', "search_text:saldo", 'search_text:"transfer gagal"',
               "search_text:dana"]
    same = {q: (count(ORIG, q), count(sea, q)) for q in queries}
    check(all(a == b for a, b in same.values()), f"tìm kiếm giống bản gốc (gốc, đã cài): {same}")

    table = ["", "## Wordcloud theo nước (facet thô, top 8 cụm, top 3 hashtag)", "",
             "| Nước | Cụm | Hashtag |", "|---|---|---|"]
    for c in COUNTRIES:
        core = f"topic_sea_{c}"
        phrases = [(p, n) for p, n in facet(core, FIELD, 30) if not p.startswith("#")][:8]
        tags = facet(core, FIELD, 3, prefix="#")
        check(len(phrases) > 0 and len(tags) > 0, f"{core}: có cụm và hashtag")
        table.append(f"| {c} | {', '.join(f'{p} ({n})' for p, n in phrases)} | "
                     f"{', '.join(f'{p} ({n})' for p, n in tags)} |")

    doc_id = requests.post(f"{SOLR}/{sea}/select", json={"query": "*:*", "limit": 1, "fields": "id"},
                           timeout=60).json()["response"]["docs"][0]["id"]
    post(sea, [{"id": doc_id, "search_text": {"set": ["", "Uji atomic update kopi susu gula aren #KopiTest"]}}],
         commit="true")
    hit = count(sea, f'id:"{doc_id}"', term("kopi susu gula aren"), term("#kopitest"))
    check(hit == 1, f"atomic update tính lại cụm và hashtag cho doc {doc_id}")
    report += table + [""]

    report.insert(2, f"**Kết quả: {'ĐẠT' if not failures else 'LỖI: ' + '; '.join(failures)}**\n")
    (ROOT / "results" / "deploy_test.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
