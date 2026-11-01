"""引证铁律校验：每张蒸馏卡的原文引证必须能在对应章节文本中定位。"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "distilled" / "the-intelligent-investor"
CHAP = ROOT / "ingest" / "the-intelligent-investor" / "chapters"

FRONT_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
QUOTE_RE = re.compile(r"\*\*原文引证\*\*（书页 p\.(\d+)）：“(.+)”")


def normalize(s: str) -> str:
    return re.sub(r"\s+", "", s)


CARD_BLOCK_RE = re.compile(r"^---\n.*?\n---\n.*?(?=^---\n|\Z)", re.S | re.M)


def extract_cards(text: str) -> list[dict]:
    text = text.replace("\r\n", "\n")
    cards = []
    for block in CARD_BLOCK_RE.findall(text):
        m = FRONT_RE.match(block)
        if not m:
            continue
        fm = m.group(1)
        card = {"frontmatter": fm, "body": block}
        idm = re.search(r"^id:\s*(\S+)", fm, re.M)
        chm = re.search(r"^chapter:\s*(\d+)", fm, re.M)
        card["id"] = idm.group(1) if idm else "?"
        card["chapter"] = int(chm.group(1)) if chm else None
        card["quotes"] = QUOTE_RE.findall(block)
        cards.append(card)
    return cards


def check_card(card: dict, chapters: dict[int, str]) -> str | None:
    if not card["quotes"]:
        return f'{card["id"]}: 无原文引证'
    md = chapters.get(card["chapter"], "")
    norm_md = normalize(md)
    for _page, quote in card["quotes"]:
        if normalize(quote) not in norm_md:
            return f'{card["id"]}: 引证无法在章节 {card["chapter"]} 定位：“{quote[:20]}…”'
    return None


SPECIAL_CHAPTERS = {"preface.md": 0, "postscript.md": 21, "appendices.md": 22}


def load_chapters() -> dict[int, str]:
    chapters = {}
    for f in CHAP.glob("ch-*.md"):
        n = int(f.stem.split("-")[1])
        chapters[n] = f.read_text(encoding="utf-8").replace("\r\n", "\n")
    # 导言按第 0 章、后记按第 21 章、附录 1-7 按第 22 章登记（非 ch-NN 命名）
    for name, n in SPECIAL_CHAPTERS.items():
        p = CHAP / name
        if p.exists():
            chapters[n] = p.read_text(encoding="utf-8").replace("\r\n", "\n")
    return chapters


def main() -> int:
    chapters = load_chapters()
    errors = []
    for f in sorted(DIST.rglob("*.md")):
        if f.name == "INDEX.md":
            continue
        for card in extract_cards(f.read_text(encoding="utf-8")):
            err = check_card(card, chapters)
            if err:
                errors.append(err)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("all citations verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
