import pytest
from pathlib import Path

from scripts.ingest import pdf_to_book, book_to_pdf, format_chapter_md, parse_page_markers, render_page, ocr_image


def test_low_char_warning_threshold():
    from scripts.extract_chapters import is_low_char
    assert is_low_char("") and is_low_char("x" * 49)
    assert not is_low_char("x" * 50)


def test_render_pages_batch(tmp_path):
    from scripts.ingest import render_pages
    pdf = Path("scratch/ii.pdf")
    if not pdf.exists():
        pytest.skip("scratch/ii.pdf 不存在")
    outs = render_pages(pdf, [61, 62], tmp_path)
    assert len(outs) == 2 and all(o.exists() for o in outs)


PDF = Path("scratch/ii.pdf")


def test_pdf_to_book():
    assert pdf_to_book(61) == 43
    assert pdf_to_book(30) == 12


def test_book_to_pdf():
    assert book_to_pdf(123) == 141
    assert book_to_pdf(341) == 359


def test_format_chapter_md_roundtrip():
    pages = [(141, 123, "正文一"), (142, 124, "正文二")]
    md = format_chapter_md("第 8 章 投资者与市场波动", pages)
    assert md.startswith("# 第 8 章 投资者与市场波动")
    assert parse_page_markers(md) == [141, 142]
    assert "正文一" in md and "正文二" in md


@pytest.mark.slow
def test_render_and_ocr_smoke(tmp_path):
    if not PDF.exists():
        pytest.skip("scratch/ii.pdf 不存在")
    img = render_page(PDF, 61, tmp_path / "p061.png")
    assert img.exists()
    text = ocr_image(img)
    assert "第" in text and "章" in text  # 页眉"第 3 章 一个世纪的股市历史"
    assert "1871" in text               # 表 3-1 首行年份
