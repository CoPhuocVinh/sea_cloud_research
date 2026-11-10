"""So cách tách từ tiếng Thái: ThaiSegmenter (gói SEA) vs PyThaiNLP newmm vs Lucene ThaiTokenizer vs ICU.

    mvn -q compile
    uv run -q --python 3.12 --with pythainlp scripts/compare_thai_seg.py

Không có bộ tách từ chuẩn (gold) được phép dùng thương mại (BEST2010 là CC BY-NC-SA), nên đo 3 thứ:
1. Độ khớp ranh giới từ với newmm (mốc tham khảo, KHÔNG phải đáp án): precision/recall/F1 trên các vị trí
   nằm giữa 2 chữ Thái.
2. Đáp án của data tổng hợp (truth_th.json): mỗi lần một cụm/tên Thái trong đáp án xuất hiện, tokenizer có cắt
   đúng ở 2 mép cụm không, và cụm thành bao nhiêu token (wordcloud ghép tối đa 4).
3. Token rác: 1 ký tự, chỉ gồm 1 ký tự lặp (กก, ยยย), hoặc vỡ cụm ký tự (bắt đầu bằng dấu/nguyên âm đi sau,
   kết thúc bằng nguyên âm đứng trước).
Văn bản: data/holdout{,2,3}/th.json (tổng hợp) + case Thái trong src/test/resources/cases.tsv. Hashtag, URL, @ và
ký tự ngoài BMP (emoji) được thay bằng dấu cách trước khi tách để mọi tokenizer nhận cùng chuỗi, cùng offset.
Ghi results/compare_thai_seg.md.
"""

import json
import re
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

from pythainlp import __version__ as pythainlp_version
from pythainlp.tokenize import word_tokenize

ROOT = Path(__file__).resolve().parent.parent
DATA_DIRS = ["holdout", "holdout2", "holdout3"]
CONF = ROOT / "docker" / "configsets" / "sea_cloud" / "conf"
ENGINES = ["sea", "newmm", "lucene_th", "icu"]
NOISE = re.compile(r"https?://\S+|www\.\S+|#\S+|@\w+|[^\u0000-￿]|\s+")
EXAMPLES = 15


def is_thai(ch: str) -> bool:
    return "฀" <= ch <= "๿"


def is_non_starter(ch: str) -> bool:
    """Giống ThaiSegmenter.isNonStarter (Java)."""
    return "ะ" <= ch <= "ฺ" or ch == "ๅ" or "็" <= ch <= "๎"


def is_leading_vowel(ch: str) -> bool:
    return "เ" <= ch <= "ไ"


def clean(text: str) -> str:
    return NOISE.sub(" ", text).strip()


def load_texts() -> tuple[list[str], list[dict]]:
    texts, truth = {}, []
    for name in DATA_DIRS:
        folder = ROOT / "data" / name
        for doc in json.loads((folder / "th.json").read_text(encoding="utf-8")):
            text = clean(doc["search_text"][1])
            if any(is_thai(c) for c in text):
                texts.setdefault(text, None)
        truth += json.loads((folder / "truth_th.json").read_text(encoding="utf-8"))
    for line in (ROOT / "src" / "test" / "resources" / "cases.tsv").read_text(encoding="utf-8").splitlines():
        parts = line.split("\t")
        if parts[0] == "th" and len(parts) >= 3:
            texts.setdefault(clean(parts[2]), None)
    return list(texts), truth


def java_spans(texts: list[str]) -> tuple[dict[str, list[list[tuple[int, int]]]], dict[str, int]]:
    cp_file = Path(tempfile.mkstemp(suffix=".txt")[1])
    subprocess.run(["mvn", "-q", "dependency:build-classpath", f"-Dmdep.outputFile={cp_file}"], cwd=ROOT, check=True)
    classpath = f"{ROOT / 'target' / 'classes'}:{cp_file.read_text().strip()}"
    with tempfile.TemporaryDirectory() as tmp:
        src, out = Path(tmp) / "in.txt", Path(tmp) / "out.tsv"
        src.write_text("\n".join(texts) + "\n", encoding="utf-8")
        subprocess.run(["java", "-cp", classpath, str(ROOT / "scripts" / "ThaiTokenDump.java"), str(src), str(out),
                        str(CONF / "dict" / "thai_extra.txt")], check=True)
        spans: dict[str, list[list[tuple[int, int]]]] = {}
        times: dict[str, int] = {}
        for line in out.read_text(encoding="utf-8").splitlines():
            engine, key, value = line.split("\t")
            if engine == "#time":
                times[key] = int(value)
                continue
            pairs = [tuple(map(int, p.split(":"))) for p in value.split(",")] if value else []
            spans.setdefault(engine, []).append(pairs)
    cp_file.unlink()
    return spans, times


def newmm_spans(texts: list[str]) -> tuple[list[list[tuple[int, int]]], int]:
    t0 = time.perf_counter()
    out = []
    for text in texts:
        pos, spans = 0, []
        for tok in word_tokenize(text, engine="newmm", keep_whitespace=True):
            if tok.strip():
                spans.append((pos, pos + len(tok)))
            pos += len(tok)
        if pos != len(text):
            raise SystemExit(f"newmm không giữ nguyên văn bản: {text!r}")
        out.append(spans)
    return out, round((time.perf_counter() - t0) * 1000)


def thai_tokens(text: str, spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    return [(s, e) for s, e in spans if all(is_thai(c) for c in text[s:e])]


def inner_boundaries(text: str, spans: list[tuple[int, int]]) -> set[int]:
    """Ranh giới token nằm giữa 2 chữ Thái liền nhau (chỗ duy nhất các tokenizer có thể khác nhau)."""
    cuts = {p for s, e in spans for p in (s, e)}
    return {p for p in cuts if 0 < p < len(text) and is_thai(text[p - 1]) and is_thai(text[p])}


def junk_kind(token: str) -> str | None:
    if len(token) == 1:
        return "1 ký tự"
    if len(set(token)) == 1:
        return "ký tự lặp"
    if is_non_starter(token[0]) or is_leading_vowel(token[-1]):
        return "vỡ cụm ký tự"
    return None


def thai_variants(truth: list[dict]) -> list[str]:
    seen = {v for item in truth for v in item["variants"] if v and all(is_thai(c) for c in v)}
    return sorted(seen, key=len, reverse=True)


def answer_key(text: str, spans: list[tuple[int, int]], variants: list[str]) -> list[tuple[bool, int]]:
    """Mỗi lần xuất hiện của cụm đáp án: (cắt đúng 2 mép?, số token phủ cụm)."""
    cuts = {p for s, e in spans for p in (s, e)}
    result, taken = [], set()
    for v in variants:
        for m in re.finditer(re.escape(v), text):
            s, e = m.start(), m.end()
            if any(p in taken for p in range(s, e)):
                continue  # đã tính trong một biến thể dài hơn
            taken.update(range(s, e))
            left_ok = s == 0 or not is_thai(text[s - 1]) or s in cuts
            right_ok = e == len(text) or not is_thai(text[e]) or e in cuts
            covering = sum(1 for a, b in spans if a < e and b > s)
            result.append((left_ok and right_ok, covering))
    return result


def show(text: str, spans: list[tuple[int, int]]) -> str:
    return " · ".join(text[s:e] for s, e in thai_tokens(text, spans))


def evaluate(texts, spans_by_engine, variants) -> list[dict]:
    rows = []
    ref = spans_by_engine["newmm"]
    for engine in ENGINES:
        tp = fp = fn = 0
        tokens, junk, types = 0, Counter(), set()
        key = []
        for i, text in enumerate(texts):
            spans = spans_by_engine[engine][i]
            mine, theirs = inner_boundaries(text, spans), inner_boundaries(text, ref[i])
            tp, fp, fn = tp + len(mine & theirs), fp + len(mine - theirs), fn + len(theirs - mine)
            for s, e in thai_tokens(text, spans):
                tok = text[s:e]
                tokens += 1
                types.add(tok)
                kind = junk_kind(tok)
                if kind:
                    junk[kind] += 1
            key += answer_key(text, spans, variants)
        p, r = tp / max(1, tp + fp), tp / max(1, tp + fn)
        edges = sum(ok for ok, _ in key)
        rows.append({
            "engine": engine,
            "P vs newmm": f"{p:.3f}", "R vs newmm": f"{r:.3f}", "F1 vs newmm": f"{2 * p * r / max(1e-9, p + r):.3f}",
            "đáp án: cắt đúng 2 mép": f"{edges}/{len(key)} ({edges / max(1, len(key)):.1%})",
            "đáp án: đúng mép và ≤4 token": f"{sum(ok and n <= 4 for ok, n in key) / max(1, len(key)):.1%}",
            "token Thái": tokens, "từ khác nhau": len(types),
            "rác / 1000 token": f"{1000 * sum(junk.values()) / max(1, tokens):.1f}",
            "rác theo loại": ", ".join(f"{k} {v}" for k, v in junk.most_common()) or "-",
        })
    return rows


def disagreements(texts, spans_by_engine, variants, limit: int) -> list[str]:
    """Câu mà sea và newmm tách khác nhau, ưu tiên câu có cụm đáp án, mỗi kiểu khác biệt lấy 1 ví dụ."""
    out, seen = [], set()
    for want_variant in (True, False):
        for i, text in enumerate(texts):
            if len(out) >= limit:
                return out
            sea, ref = spans_by_engine["sea"][i], spans_by_engine["newmm"][i]
            diff = inner_boundaries(text, sea) ^ inner_boundaries(text, ref)
            if not diff or any(v in text for v in variants) != want_variant:
                continue
            signature = frozenset(text[max(0, p - 4):p + 4] for p in diff)
            if signature & seen:
                continue
            seen |= signature
            row = [f"| `{text}` | {show(text, sea)} | {show(text, ref)} | {show(text, spans_by_engine['lucene_th'][i])} |"]
            out += row
    return out


def table(rows: list[dict]) -> str:
    cols = list(rows[0])
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(str(r[c]) for c in cols) + " |" for r in rows]
    return "\n".join(lines)


def main() -> None:
    texts, truth = load_texts()
    variants = thai_variants(truth)
    print(f"{len(texts)} câu khác nhau, {len(variants)} biến thể cụm đáp án tiếng Thái", file=sys.stderr)
    spans, times = java_spans(texts)
    spans["newmm"], times["newmm"] = newmm_spans(texts)
    rows = evaluate(texts, spans, variants)
    speed = [{"engine": e, "ms cho cả bộ": times[e], "câu/giây": round(len(texts) / max(1, times[e]) * 1000)}
             for e in ENGINES]
    report = [
        "# Tách từ tiếng Thái: ThaiSegmenter vs PyThaiNLP newmm vs Lucene ThaiTokenizer vs ICU",
        "",
        f"Sinh bởi `scripts/compare_thai_seg.py`. {len(texts)} câu Thái khác nhau từ data tổng hợp "
        f"`data/holdout{{,2,3}}/th.json` + case Thái trong `cases.tsv`; PyThaiNLP {pythainlp_version}.",
        "",
        "- `sea`: `ScriptRoutingTokenizer` của gói (ThaiSegmenter + `dict/thai_extra.txt`, ICU cho chữ không phải Thái).",
        "- `newmm`: PyThaiNLP `word_tokenize(engine=\"newmm\")`, Python, không chạy trong Solr. **Là mốc tham khảo, "
        "không phải đáp án** nên P/R/F1 chỉ nói hai bên giống nhau bao nhiêu.",
        "- `lucene_th`: `org.apache.lucene.analysis.th.ThaiTokenizer` (BreakIterator của JDK, không thêm từ được).",
        "- `icu`: `ICUTokenizer` (từ điển Thái có sẵn của ICU4J, không thêm từ được).",
        "",
        "Cột *đáp án* dùng `truth_th.json`: mỗi lần một cụm/tên Thái của đáp án (kể cả biến thể kéo dài, sai chính tả) "
        "xuất hiện, tokenizer phải cắt ở đúng 2 mép thì wordcloud mới ghép lại được cụm đó; wordcloud ghép tối đa 4 token.",
        "",
        "## Kết quả",
        "",
        table(rows),
        "",
        "## Tốc độ (1 luồng, gồm cả phần chữ Latin)",
        "",
        table(speed),
        "",
        "## Ví dụ sea và newmm tách khác nhau",
        "",
        "| Câu | sea | newmm | lucene_th |",
        "|---|---|---|---|",
        *disagreements(texts, spans, variants, EXAMPLES),
        "",
    ]
    (ROOT / "results" / "compare_thai_seg.md").write_text("\n".join(report), encoding="utf-8")
    print(table(rows))
    print(table(speed))
    print("wrote results/compare_thai_seg.md")


if __name__ == "__main__":
    main()
