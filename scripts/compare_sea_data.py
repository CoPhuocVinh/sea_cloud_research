"""Chấm wordcloud trên data SEA tổng hợp theo đáp án (data/synthetic/truth_<cc>.json).

    uv run --with requests scripts/compare_sea_data.py

4 cách so cho mỗi nước:
- baseline : data_<cc>.search_text_icu — chain topic_global (ICU + ICUFolding) + shingle 2–4
- 2 pha    : vocab_<cc>.cloud_phrases — chỉ index cụm trong từ vựng đã đào (mine_vocabulary.py)
- 3 kiểu stoplist biên, cùng analyzer, 2000 cụm đầu qua phrase_vocab.clean ở tầng truy vấn:
  bản dùng thật = chỉ từ nối (cloud_phrases), lớn cũ (cloud_phrases_full),
  không có (cloud_phrases_nostop)
Mỗi mục top K: hit (cụm đã cài; tên > 4 từ thì 1 cửa sổ 4 từ bất kỳ), dup (biến thể/cửa sổ khác của cụm đã tính),
fragment (mảnh con của cụm đã cài), noise. Ghi results/report_sea_synthetic.md.
"""

import argparse
import json
import re
from pathlib import Path

import requests

from phrase_vocab import clean

SOLR = "http://localhost:8985/solr"
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "synthetic"
THAI_DICTS = [ROOT / "src/main/resources/vn/younet/wordcloud/words_th.txt",
              ROOT / "docker/configsets/sea_cloud/conf/dict/thai_extra.txt"]
COUNTRIES = ["id", "ms", "tl", "sg", "th"]
TOP = 50
CLEAN_POOL = 2000  # số cụm đầu đưa vào phrase_vocab.clean (như pha đào từ vựng, nhưng ở tầng truy vấn)
STOPLIST_VARIANTS = [("stoplist dùng thật + làm sạch", "cloud_phrases"),
                     ("stoplist lớn cũ + làm sạch", "cloud_phrases_full"),
                     ("không stoplist + làm sạch", "cloud_phrases_nostop")]
MAX_WORDS = 4
THAI = re.compile("[\u0E00-\u0E7F]")
LANG = ROOT / "docker/configsets/sea_cloud/conf/lang"
NEVER_STOP = ROOT / "resources_src/extra/never_stop.txt"


def facet(core: str, field: str, limit: int) -> tuple[list[tuple[str, int]], int]:
    body = {"query": "*:*", "limit": 0,
            "facet": {"c": {"type": "terms", "field": field, "limit": limit, "mincount": 1, "numBuckets": True}}}
    r = requests.post(f"{SOLR}/{core}/select", json=body, timeout=600)
    r.raise_for_status()
    f = r.json()["facets"]["c"]
    return [(b["val"], b["count"]) for b in f["buckets"]], f["numBuckets"]


def norm(text: str) -> str:
    """So với đáp án: bỏ dấu nháy và dấu nối vô hình U+200B của cụm Thái (đáp án Thái viết liền)."""
    return re.sub(r"\s+", " ", re.sub(r"['’\u200b]", "", text.lower())).strip()


def windows(phrase: str, size: int) -> set[str]:
    w = phrase.split(" ")
    return {" ".join(w[i:i + size]) for i in range(len(w) - size + 1)}


def sub_phrases(phrase: str) -> set[str]:
    w = phrase.split(" ")
    return {" ".join(w[i:j]) for i in range(len(w)) for j in range(i + 2, len(w) + 1) if j - i < len(w)}


class Truth:
    def __init__(self, data_dir: Path, country: str, thai_words: set[str]):
        self.items = json.loads((data_dir / f"truth_{country}.json").read_text(encoding="utf-8"))
        self.thai = country == "th"
        self.accept: list[set[str]] = []
        self.fragments: list[set[str]] = []
        self.eligible: list[bool] = []
        for t in self.items:
            forms = {norm(v) for v in t["variants"]} | {norm(t["canonical"])}
            accept = set(forms)
            for f in forms:
                if len(f.split(" ")) > MAX_WORDS:
                    accept |= windows(f, MAX_WORDS)
            frags = set().union(*(sub_phrases(f) for f in forms)) - accept
            self.accept.append(accept)
            self.fragments.append(frags)
            canonical = norm(t["canonical"])
            # Cụm Latin phải >= 2 từ; cụm Thái (viết liền) phải không phải 1 từ trong từ điển. Tên Latin 1 từ trong
            # topic Thái (gmmtv, mistine) không thể là cụm 2–4 từ nên không tính.
            if THAI.search(canonical):
                self.eligible.append(canonical not in thai_words)
            else:
                self.eligible.append(len(canonical.split(" ")) >= 2)

    def label(self, phrase: str) -> tuple[str, int | None]:
        p = norm(phrase)
        owner = next((i for i, a in enumerate(self.accept) if p in a), None)
        if owner is not None:
            return "match", owner
        if any(p in f for f in self.fragments) or (self.thai and any(p in c for a in self.accept for c in a)):
            return "fragment", None
        return "noise", None

    def classify(self, items: list[tuple[str, int]]) -> dict:
        seen, counts = set(), {"hit": 0, "dup": 0, "fragment": 0, "noise": 0}
        for phrase, _ in items[:TOP]:
            kind, owner = self.label(phrase)
            if kind == "match":
                counts["dup" if owner in seen else "hit"] += 1
                seen.add(owner)
            else:
                counts[kind] += 1
        eligible = [i for i, e in enumerate(self.eligible) if e]
        found = [i for i in eligible if i in seen]
        counts["recall"] = f"{len(found)}/{len(eligible)}"
        counts["missed"] = [self.items[i]["canonical"] for i in eligible if i not in seen]
        return counts


def load_thai_words() -> set[str]:
    words = set()
    for path in THAI_DICTS:
        words |= {w.strip() for w in path.read_text(encoding="utf-8").splitlines() if w.strip() and not w.startswith("#")}
    return words


def word_list(path: Path) -> set[str]:
    words = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            words.update(w.lower() for w in line.split())
    return words


def relaxed_rule(phrase: str, negations: set[str], tails: set[str]) -> str | None:
    """Luật nới nào cho cụm này qua được: mở đầu bằng từ phủ định, hoặc kết thúc bằng từ nhấn (tail)."""
    if THAI.search(phrase):
        neg = next((n for n in negations if THAI.search(n) and phrase.startswith(n)), None)
        tail = next((t for t in tails if phrase.endswith(t) and phrase != t), None)
    else:
        w = phrase.split(" ")
        neg = w[0] if w[0] in negations else None
        tail = w[-1] if len(w) > 1 and w[-1] in tails else None
    return f"phủ định '{neg}'" if neg else f"từ cuối '{tail}'" if tail else None


def relaxation_rows(c: str, truth: "Truth", items: list[tuple[str, int]], negations: set[str]) -> list[str]:
    tails = word_list(LANG / f"cloud_tail_{c}.txt")
    rows = []
    for phrase, count in items[:TOP]:
        rule = relaxed_rule(phrase, negations, tails)
        if rule:
            kind, _ = truth.label(phrase)
            rows.append(f"| {c} | {phrase} ({count}) | {rule} | {'đáp án' if kind == 'match' else kind} |")
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=Path, default=DATA)
    ap.add_argument("--report", type=Path, default=ROOT / "results" / "report_sea_synthetic.md")
    args = ap.parse_args()
    thai_words = load_thai_words()
    negations = word_list(NEVER_STOP)
    relaxed = ["| Nước | Cụm (mention) trong top 50 của 2 pha | Lọt nhờ luật | Là |", "|---|---|---|---|"]
    out = ["# Wordcloud trên data SEA TỔNG HỢP: baseline topic_global vs analyzer mới",
           "", f"Sinh bởi `scripts/compare_sea_data.py`. Data: `{args.data_dir}` (sinh bởi "
           "`scripts/gen_sea_data.py`, seed cố định). **Không phải data thật.** Gazetteer tắt ở mọi core đánh giá.",
           "", f"Chấm trên top {TOP}: hit / dup / fragment / noise (số mục), recall = số cụm đáp án (≥ 2 từ) có mặt.", ""]
    summary = ["| Nước | Cách | distinct | recall | hit | dup | fragment | noise |", "|---|---|---|---|---|---|---|---|"]
    details = []
    for c in COUNTRIES:
        truth = Truth(args.data_dir, c, thai_words)
        base, base_n = facet(f"data_{c}", "search_text_icu", TOP)
        vocab, vocab_n = facet(f"vocab_{c}", "cloud_phrases", TOP)
        variants = [("baseline topic_global", base, base_n), ("2 pha (từ vựng)", vocab, vocab_n)]
        for name, field in STOPLIST_VARIANTS:
            items, n = facet(f"data_{c}", field, CLEAN_POOL)
            variants.append((name, sorted(clean(dict(items)).items(), key=lambda kv: -kv[1]), n))
        for name, items, n in variants:
            r = truth.classify(items)
            summary.append(f"| {c} | {name} | {n} | {r['recall']} | {r['hit']} | {r['dup']} | {r['fragment']} | {r['noise']} |")
        relaxed += relaxation_rows(c, truth, vocab, negations)
        missed = truth.classify(vocab)["missed"]
        details += [f"### {c}", "", f"Cụm đáp án mà **2 pha** bỏ sót: {', '.join(missed) or '—'}", "",
                    "| # | " + " | ".join(v[0] for v in variants) + " |", "|---|" + "---|" * len(variants)]
        for i in range(15):
            cells = [f"{v[1][i][0]} ({v[1][i][1]})" if i < len(v[1]) else "" for v in variants]
            details.append(f"| {i + 1} | " + " | ".join(cells) + " |")
        details.append("")
    report = out + summary + ["", "## Cụm lọt vào nhờ luật nới (phủ định / từ nhấn cuối cụm)", "",
                              "Đo phần hại của luật nới: cụm nào trong top 50 của 2 pha chỉ có mặt nhờ luật đó, và nó là "
                              "đáp án hay rác.", ""] + relaxed + ["", "## Top 15 theo nước", ""] + details
    args.report.write_text("\n".join(report), encoding="utf-8")
    print("\n".join(summary))


if __name__ == "__main__":
    main()
