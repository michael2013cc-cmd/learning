# 金融著作蒸馏系统 P1（样章验证）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 对《聪明的投资者》第 1/8/20 章完成"扫描 PDF → 章节文本 → 分层蒸馏卡片 → 引证校验 → 8 题质量门"的完整样章验证，定稿蒸馏 schema。

**Architecture:** Ingest 层用 PyMuPDF 渲染 + RapidOCR 提取章节文本（页码标记内嵌 markdown）；Distill 层按 `docs/schema.md` 模板产出原则/模型/清单/框架四类卡片，引证铁理由 `tests/validate_citations.py` 自动校验；质量门用 8 题测试集人工+自动结合验收。

**Tech Stack:** Python 3.11 (anaconda)、PyMuPDF 1.28.2、rapidocr-onnxruntime、pytest、git。源文件：`scratch/ii.pdf`（已核实：人邮 2011 中译本，原本第 4 版，PDF 页 = 书页 + 18，扫描质量优秀）。

**Spec：** `docs/superpowers/specs/2026-08-29-finance-distiller-design.md`

---

## File Structure

| 文件 | 职责 |
|---|---|
| `scripts/ingest.py` | 页码映射、页面渲染、OCR、章节 markdown 格式化与解析 |
| `scripts/extract_chapters.py` | CLI：按章节区间批量提取，产出 chapters/*.md 与 page-map.md |
| `tests/test_ingest.py` | ingest 纯逻辑单元测试 |
| `tests/validate_citations.py` | 引证铁律校验器：卡片引文必须能在对应章节文本中定位 |
| `docs/schema.md` | 蒸馏卡片 schema 模板（四类卡片 + 现代性标注 + 引证格式） |
| `ingest/the-intelligent-investor/chapters/ch-{01,08,20}.md` | 样章文本（带页码标记） |
| `ingest/the-intelligent-investor/page-map.md` | 章节↔书页↔PDF 页映射 |
| `distilled/the-intelligent-investor/book.json` | 元数据 |
| `distilled/the-intelligent-investor/{principles,models,checklists,frameworks}/` | 蒸馏卡片 |
| `distilled/the-intelligent-investor/INDEX.md` | 卡片索引 |
| `tests/question-set.md` | P1 质量门 8 题 |
| `tests/p1-validation.md` | 验证结果记录 |

**P1 范围说明：** `preface-appendices/`（巴菲特序+附录蒸馏）与 QMind 入库、`graham-advisor` skill 属 P2 范围，本计划不覆盖。

---

### Task 1: Ingest 核心逻辑（TDD）

**Files:**
- Create: `scripts/ingest.py`
- Test: `tests/test_ingest.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_ingest.py
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
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_ingest.py -v`
Expected: FAIL（ModuleNotFoundError: scripts.ingest）

- [ ] **Step 3: 写最小实现**

```python
# scripts/ingest.py
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


def format_chapter_md(title: str, pages: list[tuple[int, int, str]], offset: int = DEFAULT_OFFSET) -> str:
    parts = [f"# {title}\n"]
    for pdf_page, book_page, text in pages:
        parts.append(f"\n<!-- page: pdf={pdf_page} book={book_page} -->\n\n{text.strip()}\n")
    return "\n".join(parts)


def parse_page_markers(md: str) -> list[int]:
    return [int(m) for m in re.findall(r"<!-- page: pdf=(\d+) book=(\d+) -->", md)]
```

同时创建 `scripts/__init__.py`（空文件）使 `scripts` 可导入；创建 `pytest.ini`：

```ini
[pytest]
markers =
    slow: 集成冒烟测试（需要 scratch/ii.pdf 与 OCR 模型）
pythonpath = .
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/test_ingest.py -v`
Expected: 3 passed

- [ ] **Step 5: 提交**

```bash
git add scripts/ingest.py scripts/__init__.py tests/test_ingest.py
git commit -m "feat(ingest): 页码映射与章节 markdown 格式化核心"
```

---

### Task 2: 渲染 + OCR 冒烟测试

**Files:**
- Modify: `scripts/ingest.py`（无改动，仅使用）
- Test: `tests/test_ingest.py`（追加集成冒烟测试，标记 `@pytest.mark.slow`）

- [ ] **Step 1: 安装 rapidocr**

Run: `pip install rapidocr-onnxruntime`
Expected: Successfully installed

- [ ] **Step 2: 追加冒烟测试**

```python
# tests/test_ingest.py 追加
import pytest
from pathlib import Path
from scripts.ingest import render_page, ocr_image

PDF = Path("scratch/ii.pdf")


@pytest.mark.slow
def test_render_and_ocr_smoke(tmp_path):
    if not PDF.exists():
        pytest.skip("scratch/ii.pdf 不存在")
    img = render_page(PDF, 61, tmp_path / "p061.png")
    assert img.exists()
    text = ocr_image(img)
    assert "第" in text and "章" in text  # 页眉"第 3 章 一个世纪的股市历史"
    assert "1871" in text               # 表 3-1 首行年份
```

- [ ] **Step 3: 运行冒烟测试**

Run: `python -m pytest tests/test_ingest.py -v -m slow`
Expected: 1 passed（首跑会下载 ONNX 模型，可能耗时 1-2 分钟）

- [ ] **Step 4: 提交**

```bash
git add tests/test_ingest.py
git commit -m "test(ingest): 渲染+OCR 冒烟测试"
```

---

### Task 3: 章节提取 CLI + 提取三个样章

**Files:**
- Create: `scripts/extract_chapters.py`
- Create: `ingest/the-intelligent-investor/chapters/ch-01.md`、`ch-08.md`、`ch-20.md`
- Create: `ingest/the-intelligent-investor/page-map.md`

- [ ] **Step 1: 写提取 CLI**

```python
# scripts/extract_chapters.py
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
    ("ch-08", "第 8 章 投资者与市场波动", 141, 166),
    ("ch-20", "第 20 章 作为投资中心思想的“安全边际”", 359, 371),
]


def extract(name: str, title: str, start: int, end: int) -> Path:
    pages = []
    with tempfile.TemporaryDirectory() as tmp:
        for p in range(start, end + 1):
            img = render_page(PDF, p, Path(tmp) / f"p{p:03d}.png")
            text = ocr_image(img)
            pages.append((p, pdf_to_book(p), text))
            print(f"  ocr pdf p{p} -> {len(text)} chars", file=sys.stderr)
    out = OUT / "chapters" / f"{name}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(format_chapter_md(title, pages), encoding="utf-8")
    return out


def main() -> None:
    targets = sys.argv[1:] or [c[0] for c in CHAPTERS]
    for name, title, start, end in CHAPTERS:
        if name in targets:
            print(f"extracting {name} ...", file=sys.stderr)
            extract(name, title, start, end)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 提取三个样章**

Run: `python -m scripts.extract_chapters`
Expected: 生成 `ingest/the-intelligent-investor/chapters/ch-{01,08,20}.md`，stderr 每页输出字符数 > 100（若某页 < 50 字符记为 OCR 失败页）

- [ ] **Step 3: OCR 质量抽检（质量门）**

用 Read 工具查看 `scratch/pdf_check/p061.png`（视觉真值），与 `ch-01.md` 中对应页文本人工比对 2 页（ch-01 任取 2 页）。判定标准：单页错字 ≤ 3 且无整句缺失 = 通过。
- 通过 → 继续。
- 不通过 → 在 `docs/p1-notes.md` 记录"OCR 不合格，样章改视觉阅读"，并用 Read 工具逐页（每批 ≤ 6 页图片，渲染到 `scratch/vision/`）视觉转录覆盖对应 `ch-NN.md`。

- [ ] **Step 4: 写 page-map.md**

```markdown
# 页码映射（聪明的投资者，人邮 2011，原本第 4 版）

偏移：PDF 页 = 书页 + 18

| 章节 | 书页起-止 | PDF 页起-止 |
|---|---|---|
| 导言 本书的目的 | 1-11 | 19-29 |
| 第 1 章 投资与投机 | 12-28 | 30-46 |
| 第 2 章 投资者与通货膨胀 | 29-40 | 47-58 |
| 第 3 章 一个世纪的股市历史 | 41-56 | 59-74 |
| 第 4 章 防御型投资者的投资组合策略 | 57-72 | 75-90 |
| 第 5 章 防御型投资者与普通股 | 73-84 | 91-102 |
| 第 6 章 积极型投资者的证券组合策略：被动的方法 | 85-97 | 103-115 |
| 第 7 章 积极型投资者的证券组合策略：主动的方法 | 98-122 | 116-140 |
| 第 8 章 投资者与市场波动 | 123-148 | 141-166 |
| 第 9 章 基金投资 | 149-166 | 167-184 |
| 第 10 章 投资者与投资顾问 | 167-182 | 185-200 |
| 第 11 章 普通投资者证券分析的一般方法 | 183-204 | 201-222 |
| 第 12 章 对每股利润的思考 | 205-216 | 223-234 |
| 第 13 章 对四家上市公司的比较 | 217-226 | 235-244 |
| 第 14 章 防御型投资者的股票选择 | 227-245 | 245-263 |
| 第 15 章 积极型投资者的股票选择 | 246-268 | 264-286 |
| 第 16 章 可转换证券及认股权证 | 269-284 | 287-302 |
| 第 17 章 四个非常有启发的案例 | 285-301 | 303-319 |
| 第 18 章 对八组公司的比较 | 302-331 | 320-349 |
| 第 19 章 股东与管理层：股息政策 | 332-340 | 350-358 |
| 第 20 章 作为投资中心思想的“安全边际” | 341-353 | 359-371 |
| 后记 | 354-356 | 372-374 |
| 附录 1-7 | 357-404 | 375-422 |
```

- [ ] **Step 5: 提交**

```bash
git add scripts/extract_chapters.py ingest/
git commit -m "feat(ingest): 样章提取 CLI 与三章文本、页码映射"
```

---

### Task 4: book.json 元数据

**Files:**
- Create: `distilled/the-intelligent-investor/book.json`

- [ ] **Step 1: 写元数据**

```json
{
  "id": "the-intelligent-investor",
  "title_zh": "聪明的投资者",
  "title_en": "The Intelligent Investor",
  "author": "Benjamin Graham",
  "translator": ["王中华", "黄一义"],
  "edition": "原本第 4 版（1973 修订版）中文译本",
  "publisher": "人民邮电出版社",
  "published": "2011-07",
  "isbn": "978-7-115-25369-9",
  "language": "zh",
  "source": "扫描 PDF，422 页，无文本层，质量优秀",
  "page_offset": 18,
  "has_zweig_commentary": false,
  "distilled_at": "2026-08-29",
  "scope": "P1 样章：第 1/8/20 章"
}
```

- [ ] **Step 2: 提交**

```bash
git add distilled/the-intelligent-investor/book.json
git commit -m "feat(distill): 书籍元数据"
```

---

### Task 5: 蒸馏 schema 模板

**Files:**
- Create: `docs/schema.md`

- [ ] **Step 1: 写 schema 模板**

```markdown
# 蒸馏卡片 Schema（v1，P1 定稿对象）

## 通用 frontmatter

---
id: <类型前缀>-<章号两位>-<序号两位>   # P=principle, M=model, C=checklist, F=framework
type: principle | model | checklist | framework
chapter: <int>
pages: [<书页起>, <书页止>]
importance: core | important | minor
modernity: timeless | era-bound | needs-translation
---

## modernity 标注规则
- timeless：跨时代成立（如安全边际、市场先生）
- era-bound：数值/规则依赖 1960-70 年代美国市场（如具体市盈率阈值），保留但标注
- needs-translation：框架成立但数值需现代转译，必须附 **现代转译** 段

## 原则卡（principles/）

# <原则陈述，一句话>

**原则**：<完整陈述>

**原文引证**（书页 p.<N>）：“<逐字引自 chapters/ch-NN.md 的原文，≥10 字>”

**现代性说明**：<timeless 可一句；era-bound/needs-translation 必填>

**常见误读**：<可选>

## 模型卡（models/）

# <模型名，如 市场先生>

**定义**：<…>

**原文引证**（书页 p.<N>）：“<…>”

**适用场景**：<…>

**常见误用**：<…>

## 检查清单卡（checklists/）

# <清单名，如 投资vs投机自检>

**用途**：<…>

**条目**：
- [ ] <条目 1>（依据 p.<N>）
- [ ] <条目 2>（依据 p.<N>）

**原文引证**（书页 p.<N>）：“<…>”

## 框架卡（frameworks/）

# <框架名，如 安全边际估值三步>

**步骤**：1. … 2. …（每步附依据页）

**原文引证**（书页 p.<N>）：“<…>”

**时代受限项**：<列出依赖时代数据的步骤及转译>

## 铁律
无引证不立卡：每张卡至少一条 **原文引证**，引文必须能在对应章节 md 中逐字（忽略空白）定位。
```

- [ ] **Step 2: 提交**

```bash
git add docs/schema.md
git commit -m "docs: 蒸馏卡片 schema v1"
```

---

### Task 6: 引证校验器（TDD）

**Files:**
- Create: `tests/validate_citations.py`
- Test: `tests/test_validate_citations.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_validate_citations.py
from scripts.validate_citations import normalize, extract_cards, check_card

CHAPTER_MD = """# 第 1 章 投资与投机：聪明投资者的预期收益

<!-- page: pdf=30 book=12 -->

投资操作是指经过透彻分析，能够保证本金安全并获得满意回报的操作。
"""

GOOD_CARD = """---
id: P-01-01
type: principle
chapter: 1
pages: [12, 14]
importance: core
modernity: timeless
---
# 投资三要素

**原文引证**（书页 p.12）：“投资操作是指经过透彻分析，能够保证本金安全并获得满意回报的操作。”
"""

BAD_CARD = """---
id: P-01-02
type: principle
chapter: 1
pages: [12, 14]
importance: core
modernity: timeless
---
# 伪造引证

**原文引证**（书页 p.12）：“格雷厄姆从未说过这句话。”
"""


def test_normalize():
    assert normalize("a b　c\nd") == "abcd"


def test_extract_cards():
    cards = extract_cards(GOOD_CARD + "\n" + BAD_CARD)
    assert len(cards) == 2


def test_check_card_pass():
    assert check_card(extract_cards(GOOD_CARD)[0], {1: CHAPTER_MD}) is None


def test_check_card_fail():
    err = check_card(extract_cards(BAD_CARD)[0], {1: CHAPTER_MD})
    assert err is not None and "P-01-02" in err
```

- [ ] **Step 2: 运行确认失败**

Run: `python -m pytest tests/test_validate_citations.py -v`
Expected: FAIL（ModuleNotFoundError: scripts.validate_citations）

- [ ] **Step 3: 写实现**

```python
# scripts/validate_citations.py
"""引证铁律校验：每张蒸馏卡的原文引证必须能在对应章节文本中定位。"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "distilled" / "the-intelligent-investor"
CHAP = ROOT / "ingest" / "the-intelligent-investor" / "chapters"

FRONT_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
QUOTE_RE = re.compile(r"\*\*原文引证\*\*（书页 p\.(\d+)）：“(.+?)”", re.S)


def normalize(s: str) -> str:
    return re.sub(r"\s+", "", s)


def extract_cards(text: str) -> list[dict]:
    cards = []
    for block in re.split(r"(?=^---\n)", text, flags=re.M):
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


def load_chapters() -> dict[int, str]:
    chapters = {}
    for f in CHAP.glob("ch-*.md"):
        n = int(f.stem.split("-")[1])
        chapters[n] = f.read_text(encoding="utf-8")
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
```

- [ ] **Step 4: 运行确认通过**

Run: `python -m pytest tests/test_validate_citations.py -v`
Expected: 4 passed

- [ ] **Step 5: 提交**

```bash
git add scripts/validate_citations.py tests/test_validate_citations.py
git commit -m "feat(distill): 引证铁律自动校验器"
```

---

### Task 7: 蒸馏第 1 章

**Files:**
- Create: `distilled/the-intelligent-investor/principles/P-01-*.md`、`models/M-01-*.md`、`checklists/C-01-*.md`

- [ ] **Step 1: 阅读章节文本**

Read: `ingest/the-intelligent-investor/chapters/ch-01.md`（全书页 12-28）

- [ ] **Step 2: 按 docs/schema.md 写卡片**

目标产出（数量为指导区间，以内容为准）：
- principles/ 4-7 张：投资三要素定义、投资vs投机区分、防御型/进取型分类、预期收益的现实性等
- models/ 1-2 张：防御型/进取型投资者模型
- checklists/ 1-2 张：投资vs投机自检清单

每张卡：frontmatter 完整、≥1 条逐字引证、modernity 标注（本章多为 timeless；具体收益预期数字标 era-bound）。

- [ ] **Step 3: 运行校验器**

Run: `python scripts/validate_citations.py`
Expected: 若引证不匹配（OCR 文本与引文差字），修正引文为章节 md 中的实际逐字文本后重跑，直到 `all citations verified`

- [ ] **Step 4: 提交**

```bash
git add distilled/the-intelligent-investor/
git commit -m "feat(distill): 第 1 章蒸馏卡片"
```

---

### Task 8: 蒸馏第 8 章

**Files:**
- Create: `distilled/the-intelligent-investor/principles/P-08-*.md`、`models/M-08-*.md`、`frameworks/F-08-*.md`

- [ ] **Step 1: 阅读章节文本**

Read: `ingest/the-intelligent-investor/chapters/ch-08.md`（书页 123-148）

- [ ] **Step 2: 按 schema 写卡片**

目标产出：
- models/ 1-2 张：市场先生（本章核心）
- principles/ 3-5 张：波动是机会不是指示、不择时、公式计划/定投的纪律性等
- frameworks/ 1 张：利用市场波动的决策框架

modernity：本章几乎全部 timeless。

- [ ] **Step 3: 运行校验器直到通过**

Run: `python scripts/validate_citations.py`
Expected: all citations verified

- [ ] **Step 4: 提交**

```bash
git add distilled/the-intelligent-investor/
git commit -m "feat(distill): 第 8 章蒸馏卡片"
```

---

### Task 9: 蒸馏第 20 章

**Files:**
- Create: `distilled/the-intelligent-investor/principles/P-20-*.md`、`models/M-20-*.md`、`frameworks/F-20-*.md`、`checklists/C-20-*.md`

- [ ] **Step 1: 阅读章节文本**

Read: `ingest/the-intelligent-investor/chapters/ch-20.md`（书页 341-353）

- [ ] **Step 2: 按 schema 写卡片**

目标产出：
- principles/ 2-4 张：安全边际定义、安全边际与分散化/纪律的关系
- models/ 1 张：安全边际模型
- frameworks/ 1 张：安全边际估值步骤（含时代受限项转译，如债券/市盈率具体数值）
- checklists/ 1 张：买入前安全边际检查

modernity：定义 timeless；涉及具体数值处 needs-translation 并附现代转译段。

- [ ] **Step 3: 运行校验器直到通过**

Run: `python scripts/validate_citations.py`
Expected: all citations verified

- [ ] **Step 4: 提交**

```bash
git add distilled/the-intelligent-investor/
git commit -m "feat(distill): 第 20 章蒸馏卡片"
```

---

### Task 10: 整合去重 + INDEX

**Files:**
- Create: `distilled/the-intelligent-investor/INDEX.md`
- Modify: 跨章重复的卡片（合并或交叉引用）

- [ ] **Step 1: 跨章去重**

通读全部卡片：同一原则在多章出现时，保留引证最强的一张，其余删除并在保留卡 **原文引证** 下追加多页引证。

- [ ] **Step 2: 写 INDEX.md**

```markdown
# 聪明的投资者 · 蒸馏卡片索引（P1 样章）

## principles
- P-01-01 <标题> (ch.1, p.<N>, <modernity>)
- …

## models
- …

## checklists
- …

## frameworks
- …
```

（逐条列出实际卡片，一行一卡。）

- [ ] **Step 3: 全量校验**

Run: `python scripts/validate_citations.py && python -m pytest tests/ -v -m "not slow"`
Expected: all citations verified；测试全绿

- [ ] **Step 4: 提交**

```bash
git add distilled/the-intelligent-investor/INDEX.md
git commit -m "feat(distill): 卡片索引与跨章去重"
```

---

### Task 11: 质量门测试集 + 验证

**Files:**
- Create: `tests/question-set.md`
- Create: `tests/p1-validation.md`

- [ ] **Step 1: 写 8 题测试集**

```markdown
# P1 质量门测试集

## 事实检索（引证必须命中）
1. 格雷厄姆定义"投资"的三要素是什么？（期望引证 ch.1, 书页 12 附近）
2. 面对市场先生的情绪报价，投资者应持什么态度？（ch.8）
3. "安全边际"的定义与核心作用？（ch.20）

## 作者视角（回答须带引证或明说未讨论）
4. 有人追热点短线频繁交易，格雷厄姆会如何评价？（ch.1）
5. 市场大跌我想清仓，格雷厄姆会说什么？（ch.8）
6. 一只股票市盈率很低、财务稳健，是否就值得买入？（ch.20 + 现代转译）

## 决策对照（输出对照结果+引证）
7. 检查：我听了个内幕消息想全仓买入某股票。
8. 检查：我计划长期按月定投宽基指数，跌了也继续。
```

- [ ] **Step 2: 逐题作答并记录**

对每题：先检索 `distilled/`（INDEX → 卡片），按顾问规则作答（引证带书页；无依据明说"本书未讨论"；时代受限项附转译）。答案全文 + 引证定位结果写入 `tests/p1-validation.md`，格式：

```markdown
## Q1
**答案**：…
**引证**：书页 12 "…" → ch-01.md 定位 ✅/❌
```

- [ ] **Step 3: 自动核对**

Run: `python scripts/validate_citations.py`
Expected: all citations verified（p1-validation.md 中所有 ✅ 与之一致）

- [ ] **Step 4: 提交**

```bash
git add tests/question-set.md tests/p1-validation.md
git commit -m "test(p1): 质量门测试集与验证记录"
```

---

### Task 12: P1 质量门评审（用户）

**Files:**
- Create/Modify: `docs/p1-notes.md`（schema 定稿修订记录）

- [ ] **Step 1: 向用户呈现评审材料**

内容：8 题答案与引证、卡片统计（四类各几张、modernity 分布）、OCR 抽检结论、schema 在实战中暴露的问题清单。

- [ ] **Step 2: 记录用户反馈与 schema 修订**

将确认的 schema 变更写入 `docs/p1-notes.md`（v1 → v2 diff），同步更新 `docs/schema.md`。

- [ ] **Step 3: 提交并决策 P2**

```bash
git add docs/p1-notes.md docs/schema.md
git commit -m "docs: P1 质量门评审记录与 schema 定稿"
```

质量门通过 → 进入 P2（全书推进）的独立计划；不通过 → 按反馈修订 schema 后重跑 Task 7-11。
