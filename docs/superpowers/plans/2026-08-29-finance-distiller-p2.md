# P2 Implementation Plan（全书推进 + schema v2 落地）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完成 schema v2 落地与工程加固，蒸馏第 4 章并补建"防御型投资者默认策略"卡，为全书推进扫清障碍。

**Architecture:** 延续 P1 管线（ingest → distill → output）。P2 分四个阶段，**每阶段独立验收后才进入下一阶段**；P2b/c/d 在本阶段（P2a）完成后另写独立计划，避免巨型计划。

**Tech Stack:** Python 3.11、PyMuPDF 1.28.2、rapidocr-onnxruntime（onnxruntime==1.19.2、numpy==1.26.4）、pytest、QMind MCP（P2c）。

**Spec：** `docs/superpowers/specs/2026-08-29-finance-distiller-design.md`；P1 记录：`docs/p1-notes.md`；schema v2：`docs/schema.md`。

**执行约定：** 每个 task = implementer + 审查（短任务可 spec/quality 合并一次）；commit message 用 conventional commits；Bash 分类器故障时按 P1 惯例：文件落盘、controller 代提交。

---

## File Structure（P2a 涉及）

| 文件 | 职责 |
|---|---|
| `scripts/ingest.py` | 增加 `render_pages` 批量渲染（单文档句柄） |
| `scripts/extract_chapters.py` | PDF 前置检查、单页 <50 字符告警、CHAPTERS 增加 ch-04 |
| `tests/test_ingest.py` | 批量渲染/告警逻辑测试 |
| `ingest/.../chapters/ch-04.md` | 第 4 章文本（视觉抽检） |
| `distilled/.../` | 第 4 章卡片（含防御型默认策略卡，v2 字段） |
| `distilled/.../checklists/C-01-02.md`、`C-20-01.md` | 补 **正向案例** 字段 |
| `distilled/.../frameworks/F-20-01.md` | 步骤级 modernity 行内标注 |

---

### Task 1: 提交 P1 积压（前置）

- [ ] **Step 1:** Run `python scripts/validate_citations.py` → `all citations verified`
- [ ] **Step 2:** Run `python -m pytest tests/ -q` → 9 passed
- [ ] **Step 3:** 提交全部积压（P1 第 8/20 章卡片、INDEX、验证记录、p1-notes、schema v2、requirements、.gitattributes 等）：

```bash
git add -A
git -c user.name="user" -c user.email="user@local" commit -m "feat(distill): P1 收尾（8/20章卡片+INDEX+质量门+schema v2+工程配置）"
```

- [ ] **Step 4:** `git status --short` 确认干净

---

### Task 2: extract 工程加固（TDD）

**Files:** Modify `scripts/ingest.py`、`scripts/extract_chapters.py`；Test `tests/test_ingest.py`

- [ ] **Step 1: 写失败测试**（追加到 tests/test_ingest.py）

```python
def test_low_char_warning_threshold():
    from scripts.extract_chapters import is_low_char
    assert is_low_char("") and is_low_char("x" * 49)
    assert not is_low_char("x" * 50)


def test_render_pages_batch(tmp_path):
    from pathlib import Path
    from scripts.ingest import render_pages
    pdf = Path("scratch/ii.pdf")
    if not pdf.exists():
        pytest.skip("scratch/ii.pdf 不存在")
    outs = render_pages(pdf, [61, 62], tmp_path)
    assert len(outs) == 2 and all(o.exists() for o in outs)
```

- [ ] **Step 2: 运行确认失败** `python -m pytest tests/test_ingest.py -v`
- [ ] **Step 3: 实现**

`scripts/ingest.py` 追加（单文档句柄批量渲染）：

```python
def render_pages(pdf_path: Path, pdf_pages: list[int], out_dir: Path, dpi: int = 150) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(str(pdf_path))
    try:
        return [out_dir / f"p{p:03d}.png" for p in pdf_pages
                if not doc[p - 1].get_pixmap(dpi=dpi).save(str(out_dir / f"p{p:03d}.png")) or True]
    finally:
        doc.close()
```

（注：列表推导里 save 返回 None，写法以清晰为准——实现时可改为显式循环，保持可读。）

`scripts/extract_chapters.py`：
- 模块级 `def is_low_char(text: str) -> bool: return len(text) < 50`
- `main()` 开头：`if not PDF.exists(): sys.exit(f"error: {PDF} 不存在")`
- extract() 循环内：`if is_low_char(text): print(f"  WARN low-char page {p}", file=sys.stderr)`

- [ ] **Step 4: 运行测试通过** `python -m pytest tests/ -q`
- [ ] **Step 5: 提交** `git commit -m "feat(ingest): PDF 前置检查、低字符告警、批量渲染"`

---

### Task 3: 提取第 4 章 + 视觉抽检

- [ ] **Step 1:** `extract_chapters.py` 的 CHAPTERS 追加 `("ch-04", "第 4 章 防御型投资者的投资组合策略", 75, 90)`（书页 57-72）
- [ ] **Step 2:** Run `python -m scripts.extract_chapters ch-04`；记录低字符告警页
- [ ] **Step 3:** 视觉抽检 2 页（渲染 PNG + Read 比对，标准同 P1：单页错字 ≤3 且无整句缺失）；不通过则全章视觉校正并记 `docs/p1-notes.md` 新节
- [ ] **Step 4:** 提交 `feat(ingest): 第 4 章提取与抽检`

---

### Task 4: 蒸馏第 4 章（schema v2 首用）

- [ ] **Step 1:** 通读 ch-04.md；按 schema v2 写卡：principles 2-4 张（股债 25-75% 配比、再平衡纪律等）、models 0-1 张、checklists 1 张（防御型组合自检，**含正向案例字段**）、frameworks 1 张（防御型默认策略：配比/再平衡/指数化选择——即 P1 质量门待办 #4 的专题卡）
- [ ] **Step 2:** modernity：配比具体数值 era-bound/needs-translation（附现代转译：目标日期基金/再平衡阈值）；纪律性原则 timeless；步骤级行内标注首用
- [ ] **Step 3:** `python scripts/validate_citations.py` 通过
- [ ] **Step 4:** 审查（spec+quality 合并）→ 修正 → 提交 `feat(distill): 第 4 章蒸馏卡片`

---

### Task 5: v2 字段回填

- [ ] **Step 1:** C-01-02、C-20-01 补 **正向案例** 段（如"长期定投宽基指数"，引 P-08-05/F-08-01 依据）
- [ ] **Step 2:** F-20-01 各步骤补行内 era-bound/现代转译 标注
- [ ] **Step 3:** INDEX 主题索引追加第 4 章卡；校验器通过
- [ ] **Step 4:** 提交 `feat(distill): schema v2 字段回填`

---

### Task 6: P2a 验收

- [ ] **Step 1:** 全量测试 + 校验器绿；向用户呈现：第 4 章卡清单、v2 字段示例、加固效果
- [ ] **Step 2:** 用户确认后，写 P2b 计划（全书剩余 16 章 + 导言/后记/附录，按 3-4 章/批）

---

## 后续阶段里程碑（本计划不展开）

- **P2b** 全书蒸馏：16 章 + 导言/后记 + 附录 1-7（preface-appendices 层）；每批 validator + 抽卡审查
- **P2c** 产出层：QMind 入库 + `graham-advisor` skill（四子命令 + 防幻觉三条款 + 自知之明条款）
  - QMind 接口已核实（2026-08-29，mcp_get）：`add_source(notebookId, source={kind:"text", title, content≤200k})`；`retrieve(notebookId, query, topK≤100, scoreThreshold)`
  - 入库映射：每卡一个 text source；title = `II-<卡id> <卡H1>`（如 `II-P-01-01 投资的三要素定义`）；content = 卡全文（含 frontmatter，便于检索命中后直接取引证/页码/modernity）
  - 注意：QMind MCP **无创建 notebook 工具**——若「金融经典蒸馏」notebook 不存在，需用户在 QMind UI 先建，P2c 执行时先 list_notebooks 确认
  - `graham-ask` 流程：retrieve(topK=8) → 以命中卡作答 → 引证带书页；无命中明说"本书未讨论"
- **P2d** 元工厂：`book-distiller` v0（参数化 schema + 兼容扫描/文字版），换书泛化验证
