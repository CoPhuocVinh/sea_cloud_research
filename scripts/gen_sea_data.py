"""Sinh data mạng xã hội TỔNG HỢP cho 5 nước SEA từ scripts/sea_lexicon.json (tất định theo seed).

    python3 scripts/gen_sea_data.py --per-country 20000
    python3 scripts/gen_sea_data.py --lexicon scripts/sea_lexicon_holdout.json --out-dir data/holdout --seed 7

Ghi data/synthetic/<cc>.json (JSON array, cùng dạng file export: id, domain, search_text=["", text],
created_date, platform) và data/synthetic/truth_<cc>.json (đáp án: cụm đã cài + biến thể + trọng số).
Không phải data thật: dùng để đo recall/nhiễu khi biết trước đáp án.
"""

import argparse
import json
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEXICON = Path(__file__).resolve().parent / "sea_lexicon.json"
OUT = ROOT / "data" / "synthetic"
START = datetime(2026, 9, 20, tzinfo=timezone.utc)
EMOJI = ["😂", "😍", "🔥", "👍", "🥰", "😭", "🎉", "❤️"]
SEPARATORS = [". ", "! ", "!! ", ", ", "\n", "? "]
P_CAMPAIGN, P_EMOJI, P_URL, P_MENTION, P_LAUGH = 0.08, 0.3, 0.05, 0.1, 0.15
P_LOWER, P_UPPER = 0.45, 0.05


class Generator:
    def __init__(self, lex: dict, rng: random.Random):
        self.lex = lex
        self.rng = rng
        self.thai = lex.get("thai", False)

    def pick(self, items: list[dict]) -> dict:
        return self.rng.choices(items, weights=[i["weight"] for i in items])[0]

    def fillers(self, lo: int, hi: int) -> list[str]:
        return [self.rng.choice(self.lex["filler"]) for _ in range(self.rng.randint(lo, hi))]

    def sentence(self) -> list[str]:
        entity = self.pick(self.lex["entities"])["text"]
        phrase = self.rng.choice(self.pick(self.lex["phrases"])["variants"])
        template = self.rng.randrange(4)
        if template == 0:
            parts = [self.rng.choice(self.lex["openers"]), entity, *self.fillers(0, 3)]
        elif template == 1:
            parts = [*self.fillers(1, 3), phrase, *self.fillers(0, 2)]
        elif template == 2:
            parts = [entity, phrase, *self.fillers(0, 2)]
        else:
            parts = self.fillers(2, 5)
        if self.rng.random() < 0.3:
            parts.append(self.rng.choice(self.lex["closers"]))
        return parts

    def join(self, parts: list[str]) -> str:
        return ("" if self.thai else " ").join(parts)

    def recase(self, text: str) -> str:
        if self.thai:
            return text
        r = self.rng.random()
        return text.lower() if r < P_LOWER else text.upper() if r < P_LOWER + P_UPPER else text

    def hashtags(self) -> str:
        tags = [self.pick(self.lex["entities"])["hashtag"] for _ in range(self.rng.randint(0, 2))]
        if not self.thai:
            tags = [t.lower() if self.rng.random() < 0.3 else t for t in tags]
        glue = "" if self.rng.random() < 0.2 else " "
        return glue.join("#" + t for t in tags)

    def mention(self) -> str:
        if self.rng.random() < P_CAMPAIGN:
            return self.rng.choice(self.lex["campaigns"])
        sentences = [self.join(self.sentence()) for _ in range(self.rng.randint(1, 3))]
        sep = (lambda: " ") if self.thai else (lambda: self.rng.choice(SEPARATORS))
        text = sentences[0]
        for s in sentences[1:]:
            text += sep() + s
        text = self.recase(text)
        extras = []
        if self.rng.random() < P_LAUGH:
            extras.append(self.rng.choice(self.lex["laughter"]))
        if self.rng.random() < P_EMOJI:
            extras.append("".join(self.rng.choices(EMOJI, k=self.rng.randint(1, 3))))
        if self.rng.random() < P_MENTION:
            extras.append(f"@user{self.rng.randint(1, 999)}")
        if self.rng.random() < P_URL:
            extras.append(f"https://example.com/p/{self.rng.randint(1000, 9999)}#ref")
        extras.append(self.hashtags())
        return " ".join([text, *[e for e in extras if e]])


def truth(lex: dict) -> list[dict]:
    """Đáp án: thực thể + cụm, gộp theo canonical (một thực thể có thể có nhiều cách gọi)."""
    merged: dict[str, dict] = {}
    for kind, items in (("entity", lex["entities"]), ("phrase", lex["phrases"])):
        for item in items:
            variants = item["variants"] if "variants" in item else [item["text"]]
            t = merged.setdefault(item["canonical"], {"canonical": item["canonical"], "kind": kind,
                                                      "weight": 0, "variants": []})
            t["weight"] += item["weight"]
            t["variants"] = sorted(set(t["variants"]) | set(variants))
    return sorted(merged.values(), key=lambda t: -t["weight"])


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--per-country", type=int, default=20000)
    p.add_argument("--seed", type=int, default=20261022)
    p.add_argument("--lexicon", type=Path, default=LEXICON)
    p.add_argument("--out-dir", type=Path, default=OUT)
    args = p.parse_args()

    lexicon = json.loads(args.lexicon.read_text(encoding="utf-8"))
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    for country, lex in lexicon.items():
        if country.startswith("_"):
            continue
        rng = random.Random(f"{args.seed}-{country}")
        gen = Generator(lex, rng)
        docs = []
        for _ in range(args.per_country):
            created = START + timedelta(seconds=rng.randint(0, 30 * 86400))
            docs.append({
                "id": str(uuid.UUID(int=rng.getrandbits(128))),
                "domain": lex["domain"],
                "search_text": ["", gen.mention()],
                "created_date": created.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "platform": rng.randint(1, 3),
            })
        (out / f"{country}.json").write_text(json.dumps(docs, ensure_ascii=False), encoding="utf-8")
        (out / f"truth_{country}.json").write_text(json.dumps(truth(lex), ensure_ascii=False, indent=1),
                                                   encoding="utf-8")
        print(f"{country}: {len(docs)} mention, vd: {docs[1]['search_text'][1][:120]!r}")


if __name__ == "__main__":
    main()
