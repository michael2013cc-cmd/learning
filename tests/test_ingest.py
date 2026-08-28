from scripts.ingest import pdf_to_book, book_to_pdf, format_chapter_md, parse_page_markers


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
