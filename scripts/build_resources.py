"""Sinh file stopword chặn biên cụm cho từng nước vào configset.

cloud_stop_<cc>.txt (bản dùng thật, SEA): CHỈ từ nối theo loại từ ngữ pháp — liên từ, giới từ, mạo từ, trợ từ nối
  (resources_src/extra/connectors_<lang>.txt), cùng một quy tắc cho cả 5 nước.
  Theo 3 bộ đáp án độc lập: thêm đại từ / trợ từ / chỉ định từ không tăng recall cho chữ Latin (144 so với 145/158)
  và chặn nhầm "lagi gangguan ya"; sau khi sửa làm sạch cho tiếng Thái (U+200B) thì Thái 34 so với 35/39 — chênh nhỏ,
  chọn quy tắc chung. Thí nghiệm nhóm từ: resources_src/extra/groups/ (giữ làm tài liệu, không dùng).
Lý do không dùng danh sách lớn: chặn nhầm cụm có nghĩa (phủ định, từ nhấn, từ nội dung); bước làm sạch
(phrase_vocab) đã tự loại phần lớn rác.
Chỉ để so trong configset đánh giá: cloud_stop_full_<cc> (danh sách lớn cũ).
Tiếng Việt giữ danh sách cũ.

Nguồn: resources_src/lucene (Apache-2.0, từ Solr _default), resources_src/stopwords-iso (MIT),
resources_src/extra (tự soạn: stop_<cc>.txt thêm vào, remove_stop_<cc>.txt bỏ ra, never_stop.txt = từ phủ định
không bao giờ chặn, tail_<cc>.txt = từ nhấn mạnh được đứng cuối cụm → cloud_tail_<cc>.txt).
Không dùng stopwords-iso ms: đó là list tần suất báo chí, lẫn cả từ nội dung (harga, minyak, rakyat, kereta…).
Chạy lại mỗi khi sửa nguồn: python3 scripts/build_resources.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "resources_src"
OUT = ROOT / "docker" / "configsets" / "sea_cloud" / "conf" / "lang"


def words(path: Path) -> set[str]:
    """Đọc file stopword: bỏ comment (# hoặc |), mỗi dòng có thể nhiều từ cách nhau bởi khoảng trắng."""
    if not path.exists():
        return set()
    out: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("|")[0].strip()
        if not line or line.startswith("#"):
            continue
        if path.parent.name == "stopwords-iso":
            out.add(line.lower())  # mỗi dòng là 1 mục, có thể nhiều tiếng
        else:
            out.update(w.lower() for w in line.split())
    return out


def lucene(lang: str) -> set[str]:
    return words(SRC / "lucene" / f"stopwords_{lang}.txt")


def iso(lang: str) -> set[str]:
    return words(SRC / "stopwords-iso" / f"{lang}.txt")


def extra(name: str) -> set[str]:
    return words(SRC / "extra" / f"{name}.txt")


# Ngôn ngữ xuất hiện trong post của từng nước (post nào cũng trộn tiếng Anh; ms/sg trộn tiếng Hoa)
LANGS = {"id": ["id", "en"], "ms": ["ms", "en", "zh"], "tl": ["tl", "en"], "sg": ["en", "zh", "sg"], "th": ["th", "en"]}


def per_country(source) -> dict[str, set[str]]:
    """source(lang) -> tập từ; gộp theo LANGS, thêm bộ 'sea' = hợp 5 nước, bỏ từ phủ định."""
    lists = {country: set().union(*(source(lang) for lang in langs)) for country, langs in LANGS.items()}
    lists["sea"] = set().union(*lists.values())
    never = extra("never_stop")
    return {country: stop - never for country, stop in lists.items()}


def build_connectors() -> dict[str, set[str]]:
    return per_country(lambda lang: extra(f"connectors_{lang}"))


def build() -> dict[str, set[str]]:
    """Danh sách lớn cũ (Lucene + stopwords-iso + phần tự soạn)."""
    en = lucene("en") | extra("stop_en")
    lists = {
        "id": lucene("id") | extra("stop_id") | en,
        # Malay dùng chung phần lớn hư từ với Indonesia
        "ms": (lucene("id") - extra("remove_stop_ms")) | extra("stop_ms") | en | iso("zh"),
        "th": (lucene("th") - extra("remove_stop_th")) | extra("stop_th") | en,
        "tl": (iso("tl") - extra("remove_stop_tl")) | extra("stop_tl") | en,
        "sg": en | extra("stop_sg") | iso("zh"),
        "vi": extra("stop_vi") | en,
    }
    # Bộ dự phòng khi collection chưa khai báo nước: gộp 5 nước SEA (có đụng nghĩa, vd. "saya")
    lists["sea"] = set().union(*(lists[c] for c in ("id", "ms", "th", "tl", "sg")))
    never = extra("never_stop")
    return {country: stop - never for country, stop in lists.items()}


def build_tails() -> dict[str, set[str]]:
    tails = {c: extra(f"tail_{c}") for c in ("id", "ms", "th", "tl", "sg", "vi")}
    tails["sea"] = set().union(*(tails[c] for c in ("id", "ms", "th", "tl", "sg")))
    return tails


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    full = build()
    production = {**build_connectors(), "vi": full["vi"]}
    outputs = {f"cloud_stop_{c}": s for c, s in production.items()}
    outputs |= {f"cloud_stop_full_{c}": s for c, s in full.items() if c != "vi"}
    for name, stop in outputs.items():
        header = f"# Sinh bởi scripts/build_resources.py — không sửa tay. {name}\n"
        (OUT / f"{name}.txt").write_text(header + "\n".join(sorted(stop)) + "\n", encoding="utf-8")
        print(f"{name}.txt: {len(stop)} mục")
    for country, tail in build_tails().items():
        header = f"# Sinh bởi scripts/build_resources.py — không sửa tay. Từ được đứng cuối cụm, nước: {country}\n"
        (OUT / f"cloud_tail_{country}.txt").write_text(header + "\n".join(sorted(tail)) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
