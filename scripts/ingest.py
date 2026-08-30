"""Ingest 层：扫描 PDF 的页码映射、渲染、OCR 与章节 markdown 格式化。"""
from __future__ import annotations

import re
from pathlib import Path

import pymupdf

DEFAULT_OFFSET = 18  # 已核实：PDF 页 = 书页 + 18


def pdf_to_book(pdf_page: int, offset: int = DEFAULT_OFFSET) -> int:
    return pdf_page - offset


def book_to_pdf(book_page: int, offset: int = DEFAULT_OFFSET) -> int:
    return book_page + offset


def render_page(pdf_path: Path, pdf_page: int, out_path: Path, dpi: int = 150) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(str(pdf_path))
    try:
        pix = doc[pdf_page - 1].get_pixmap(dpi=dpi)
        pix.save(str(out_path))
    finally:
        doc.close()
    return out_path


def ocr_image(image_path: Path) -> str:
    from rapidocr_onnxruntime import RapidOCR

    result, _ = RapidOCR()(str(image_path))
    if not result:
        return ""
    return "\n".join(line[1] for line in result)


def format_chapter_md(title: str, pages: list[tuple[int, int, str]]) -> str:
    parts = [f"# {title}\n"]
    for pdf_page, book_page, text in pages:
        parts.append(f"\n<!-- page: pdf={pdf_page} book={book_page} -->\n\n{text.strip()}\n")
    return "\n".join(parts)


def parse_page_markers(md: str) -> list[int]:
    return [int(pdf) for pdf, _book in re.findall(r"<!-- page: pdf=(\d+) book=(\d+) -->", md)]


def render_pages(pdf_path: Path, pdf_pages: list[int], out_dir: Path, dpi: int = 150) -> list[Path]:
    """Batch-render multiple PDF pages to PNG files using a single document handle."""
    out_dir.mkdir(parents=True, exist_ok=True)
    outs: list[Path] = []
    doc = pymupdf.open(str(pdf_path))
    try:
        for p in pdf_pages:
            out = out_dir / f"p{p:03d}.png"
            doc[p - 1].get_pixmap(dpi=dpi).save(str(out))
            outs.append(out)
    finally:
        doc.close()
    return outs
