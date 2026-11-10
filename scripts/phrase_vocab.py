"""Hậu xử lý danh sách cụm (cụm -> số mention): một nguồn duy nhất cho mine_vocabulary và các script so sánh.

Từ trong cụm cách nhau bởi dấu cách, hoặc U+200B giữa 2 từ Thái (CloudPhraseFilter.THAI_JOINER) — giữ nguyên
dấu nối gốc khi ghép lại cụm con.

1. prune_subphrases: bỏ cụm con nếu một cụm dài hơn chứa nó phủ >= RATIO số mention của nó (kiểu C-value).
2. merge_overlaps: cụm dài hơn maxWords bị n-gram cắt thành các cửa sổ trượt cùng độ dài, chồng nhau L-1 từ
   và có số đếm gần bằng nhau ("datuk seri anwar ibrahim" / "seri anwar ibrahim lawat" / ...). Gom các cửa sổ
   như vậy thành nhóm và chỉ giữ cửa sổ có nhiều mention nhất.
"""

import re

RATIO = 0.8
THAI_JOINER = "\u200b"  # phải khớp CloudPhraseFilter.THAI_JOINER (Java)
_SEPARATOR = re.compile(f"([ {THAI_JOINER}])")


def split(phrase: str) -> tuple[list[str], list[str]]:
    """Tách cụm thành (các từ, các dấu nối giữa chúng)."""
    parts = _SEPARATOR.split(phrase)
    return parts[0::2], parts[1::2]


def join(words: list[str], seps: list[str], i: int, j: int) -> str:
    """Ghép lại từ words[i:j] với đúng dấu nối gốc."""
    out = words[i]
    for k in range(i + 1, j):
        out += seps[k - 1] + words[k]
    return out


def words_of(phrase: str) -> list[str]:
    return split(phrase)[0]


def sub_phrases(phrase: str) -> set[str]:
    words, seps = split(phrase)
    n = len(words)
    return {join(words, seps, i, j) for i in range(n) for j in range(i + 1, n + 1) if j - i < n}


def prune_subphrases(counts: dict[str, int], ratio: float = RATIO) -> dict[str, int]:
    """O(n·k²) với k <= 4 từ: duyệt cụm con của từng cụm thay vì so từng cặp."""
    fragments = set()
    for phrase, count in counts.items():
        for sub in sub_phrases(phrase):
            if sub in counts and count >= ratio * counts[sub]:
                fragments.add(sub)
    return {p: c for p, c in counts.items() if p not in fragments}


def _close(a: int, b: int, ratio: float) -> bool:
    return min(a, b) >= ratio * max(a, b)


def merge_overlaps(counts: dict[str, int], ratio: float = RATIO) -> dict[str, int]:
    """Gom cửa sổ cùng độ dài L chồng nhau L-1 từ có số đếm gần nhau; giữ đại diện nhiều mention nhất."""
    parent = {p: p for p in counts}

    def find(p: str) -> str:
        while parent[p] != p:
            parent[p] = parent[parent[p]]
            p = parent[p]
        return p

    by_prefix: dict[tuple[int, str], list[str]] = {}
    for phrase in counts:
        words, seps = split(phrase)
        if len(words) >= 2:
            by_prefix.setdefault((len(words), join(words, seps, 0, len(words) - 1)), []).append(phrase)
    for phrase, count in counts.items():
        words, seps = split(phrase)
        if len(words) < 2:
            continue
        for nxt in by_prefix.get((len(words), join(words, seps, 1, len(words))), []):
            if nxt != phrase and _close(count, counts[nxt], ratio):
                parent[find(nxt)] = find(phrase)

    best: dict[str, str] = {}
    for phrase in counts:
        root = find(phrase)
        if root not in best or counts[phrase] > counts[best[root]]:
            best[root] = phrase
    keep = set(best.values())
    return {p: c for p, c in counts.items() if p in keep}


def clean(counts: dict[str, int], ratio: float = RATIO) -> dict[str, int]:
    """Tỉa cụm con rồi gộp cửa sổ chồng nhau."""
    return merge_overlaps(prune_subphrases(counts, ratio), ratio)
