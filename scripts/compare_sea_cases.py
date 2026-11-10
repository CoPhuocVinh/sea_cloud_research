"""Chạy 49 case SEA qua Solr analysis API: baseline (chain topic_global + shingle) so với text_cloud_sea.

    uv run --with requests scripts/compare_sea_cases.py

Mỗi case chạy trên core của đúng nước (sea_<cc>, cùng configset, khác topic.country). Ghi results/cases_sea.md.
"""

import csv
import re
from pathlib import Path

import requests

SOLR = "http://localhost:8985/solr"
ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "src" / "test" / "resources" / "cases.tsv"
BOUNDARY = re.compile(r"[!?;\n…]|[.,:](?!\d)")
URL = re.compile(r"(?i)\b(?:https?://|www\.)\S+")
THAI_MARKS = re.compile("[ัิ-ฺ็-๎]")


def analyze(core: str, field_type: str, text: str) -> list[dict]:
    r = requests.get(f"{SOLR}/{core}/analysis/field", params={
        "analysis.fieldtype": field_type, "analysis.fieldvalue": text, "wt": "json"}, timeout=60)
    r.raise_for_status()
    stages = r.json()["analysis"]["field_types"][field_type]["index"]
    return stages[-1] if stages and isinstance(stages[-1], list) else []


def covered(text: str, token: dict) -> str:
    """Offset của Solr tính theo UTF-16 (emoji = 2 đơn vị), không theo code point của Python."""
    units = text.encode("utf-16-le")
    return units[2 * token["start"]:2 * token["end"]].decode("utf-16-le")


def crossing(text: str, tokens: list[dict]) -> int:
    masked = URL.sub(lambda m: " " * len(m.group()), text)  # dấu . : trong URL không phải ranh giới câu
    return sum(bool(BOUNDARY.search(covered(masked, t))) for t in tokens)


def lost_thai_marks(text: str, tokens: list[dict]) -> int:
    """Token mà dạng index mất dấu Thái so với đoạn văn bản gốc nó phủ."""
    return sum(len(THAI_MARKS.findall(t["text"])) < len(THAI_MARKS.findall(covered(text, t))) for t in tokens)


def main() -> None:
    rows = []
    totals = {"base": 0, "base_cross": 0, "base_thai": 0, "new": 0, "new_cross": 0, "new_thai": 0}
    for country, case, text in csv.reader(CASES.open(encoding="utf-8"), delimiter="\t"):
        core = f"sea_{country}"
        base = analyze(core, "text_cloud_icu_baseline", text)
        new = analyze(core, "text_cloud_sea", text)
        stats = {"base": len(base), "base_cross": crossing(text, base), "base_thai": lost_thai_marks(text, base),
                 "new": len(new), "new_cross": crossing(text, new), "new_thai": lost_thai_marks(text, new)}
        for k, v in stats.items():
            totals[k] += v
        rows.append(f"| {country}/{case} | {stats['base']} / {stats['base_cross']} / {stats['base_thai']} "
                    f"| {stats['new']} / {stats['new_cross']} / {stats['new_thai']} "
                    f"| {', '.join(t['text'] for t in new) or '—'} |")
    out = [
        "# 49 case SEA: baseline topic_global vs text_cloud_sea",
        "",
        "Sinh bởi `scripts/compare_sea_cases.py` trên Solr 9.10.1 (core `sea_<nước>`).",
        "Baseline = `ICUTokenizer` + `ICUFoldingFilter` (chain tìm kiếm của topic_global) + `ShingleFilter` 2–4.",
        "",
        f"**Tổng**: baseline {totals['base']} cụm, {totals['base_cross']} vượt dấu câu, {totals['base_thai']} mất dấu Thái · "
        f"mới {totals['new']} cụm, {totals['new_cross']} vượt dấu câu, {totals['new_thai']} mất dấu Thái.",
        "",
        "| Case | Baseline: cụm / vượt câu / mất dấu Thái | Mới: cụm / vượt câu / mất dấu Thái | Cụm của analyzer mới |",
        "|---|---|---|---|",
        *rows,
        "",
    ]
    (ROOT / "results" / "cases_sea.md").write_text("\n".join(out), encoding="utf-8")
    print(out[5])


if __name__ == "__main__":
    main()
