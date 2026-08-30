"""按章节区间批量提取扫描页为带页码标记的 markdown。"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from scripts.ingest import format_chapter_md, ocr_image, pdf_to_book, render_page

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "scratch" / "ii.pdf"
OUT = ROOT / "ingest" / "the-intelligent-investor"

# (文件名, 标题, 起始 PDF 页, 结束 PDF 页) —— 页码来自已核实目录
CHAPTERS = [
    ("ch-01", "第 1 章 投资与投机：聪明投资者的预期收益", 30, 46),
    ("ch-04", "第 4 章 防御型投资者的投资组合策略", 75, 90),
    ("ch-08", "第 8 章 投资者与市场波动", 141, 166),
    ("ch-20", "第 20 章 作为投资中心思想的\u201c安全边际\u201d", 359, 371),
]


def is_low_char(text: str) -> bool:
    """Return True if OCR text has fewer than 50 characters (likely a blank/image-only page)."""
    return len(text) < 50


def extract(name: str, title: str, start: int, end: int) -> Path:
    pages = []
    with tempfile.TemporaryDirectory() as tmp:
        for p in range(start, end + 1):
            img = render_page(PDF, p, Path(tmp) / f"p{p:03d}.png")
            text = ocr_image(img)
            if is_low_char(text):
                print(f"  WARN low-char page {p}", file=sys.stderr)
            pages.append((p, pdf_to_book(p), text))
            print(f"  ocr pdf p{p} -> {len(text)} chars", file=sys.stderr)
    out = OUT / "chapters" / f"{name}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(format_chapter_md(title, pages), encoding="utf-8")
    return out


def main() -> None:
    if not PDF.exists():
        sys.exit(f"error: {PDF} 不存在")
    targets = sys.argv[1:] or [c[0] for c in CHAPTERS]
    for name, title, start, end in CHAPTERS:
        if name in targets:
            print(f"extracting {name} ...", file=sys.stderr)
            extract(name, title, start, end)


if __name__ == "__main__":
    main()
