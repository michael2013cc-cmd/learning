# 交接 Spec：剩余工作（截至 2026-09-01，commit 2433b40）

> 目的：让任何接手者（人或 agent）无需口头交接即可继续本项目。先读本文，再按需读引用文档。

## 0. 项目一分钟概览

把金融经典著作（扫描件/文字版）蒸馏成结构化卡片，产出三种用途：
1. **知识库检索问答**（卡片入 QMind 知识库）
2. **作者视角决策顾问**（`graham-advisor` skill）
3. **元工厂**（`book-distiller` 元 skill，换书可复用）

管线四段：**Ingest**（PyMuPDF 渲染 + RapidOCR + 视觉校正）→ **Distill**（schema v2 分层卡片）→ **Output**（QMind 入库 + 顾问 skill）→ **Meta**（元工厂）。

当前书：《聪明的投资者》人邮 2011 中译本（原本第 4 版，无 Zweig 评论层），422 页扫描无文本层。

## 1. 当前进度

- 已完成蒸馏：**10 章**（ch-01..09、ch-20），共 **42 张卡**：principles 28、models 5、checklists 6、frameworks 3
- 工程：`scripts/ingest.py`（渲染/批量渲染/页码换算）、`scripts/extract_chapters.py`（提取 CLI，10 章已登记）、`scripts/validate_citations.py`（引证校验）、`tests/` 12 个测试全绿
- 文档：设计 `docs/superpowers/specs/2026-08-29-finance-distiller-design.md`；计划 `docs/superpowers/plans/2026-08-29-finance-distiller-p1.md`、`-p2.md`；schema `docs/schema.md`；质量审计 `docs/p1-notes.md`；用法 `docs/USAGE.md`
- GitHub：`https://github.com/michael2013cc-cmd/learning`，**当前为公开仓库**。用户 2026-08-31 说"几天后再改私有"——**约 2026-09-02 起，开工前主动提醒用户确认是否改私有**。

## 2. 接手前置（必做）

1. **源书**：`scratch/ii.pdf` 已 gitignore，不在仓库。向用户索取该 PDF（422 页扫描件）放入 `scratch/`。没有它，提取与冒烟测试都跑不了。
2. 环境：Python 3.11 + `pip install -r requirements.txt`。**勿升级** `onnxruntime`（必须 1.19.2）与 `numpy`（1.26.4）。
3. 自检三条命令：
   ```bash
   python -m pytest tests/ -q            # 12 passed
   python scripts/validate_citations.py  # all citations verified
   ```
4. 阅读顺序：本文件 → `docs/USAGE.md` → `docs/schema.md` → `docs/p1-notes.md`（翻一遍视觉校正记录，了解 OCR 缺陷形态）。

## 3. P2b 剩余：蒸馏余下 13 章 + 导言/后记/附录

### 3.1 章节清单（精确区间，勿重新推导）

| 章 | 章节标题（登记用） | 书页 | PDF 页 |
|---|---|---|---|
| ch-10 | 第 10 章 投资者与投资顾问 | 167-182 | 185-200 |
| ch-11 | 第 11 章 普通投资者证券分析的一般方法 | 183-204 | 201-222 |
| ch-12 | 第 12 章 对每股利润的思考 | 205-216 | 223-234 |
| ch-13 | 第 13 章 对四家上市公司的比较 | 217-226 | 235-244 |
| ch-14 | 第 14 章 防御型投资者的股票选择 | 227-245 | 245-263 |
| ch-15 | 第 15 章 积极型投资者的股票选择 | 246-268 | 264-286 |
| ch-16 | 第 16 章 可转换证券及认股权证 | 269-284 | 287-302 |
| ch-17 | 第 17 章 四个非常有启发的案例 | 285-301 | 303-319 |
| ch-18 | 第 18 章 对八组公司的比较 | 302-331 | 320-349 |
| ch-19 | 第 19 章 股东与管理层：股息政策 | 332-340 | 350-358 |
| preface | 导言 本书的目的 | 1-11 | 19-29 |
| postscript | 后记 | 354-356 | 372-374 |
| appendices | 附录 1-7 | 357-404 | 375-422 |

（正文 20 章中仅剩 ch-10..19；ch-01..09、ch-20 已完成。）

### 3.2 建议批次（3-4 章/批，用户偏好短任务）

- 批 3：ch-10 + ch-11 + ch-12（提取+蒸馏各自独立提交）
- 批 4：ch-13 + ch-14 + ch-15
- 批 5：ch-16 + ch-17 + ch-18（ch-18 有 30 页，注意工作量）
- 批 6：ch-19 + 导言 + 后记 + 附录（导言/后记/附录可用较轻的 preface-appendices 层：原则卡为主，篇幅短可合并处理）

批次划分非硬性，用户可调整；每批开工前简短确认即可。

### 3.3 每批标准流程（六步，勿跳步）

1. **登记**：`scripts/extract_chapters.py` 的 `CHAPTERS` 追加条目
2. **提取**：`python -m scripts.extract_chapters ch-NN …`；记录 stderr 的 low-char 告警页
3. **视觉抽检/校正**：抽 2 页比对（标准：单页错字 ≤3 且无整句缺失）；不通过则全章逐页视觉校正，在 `docs/p1-notes.md` 追加校正小节（格式照抄现有小节）。经验值：每章几乎都不通过，预算按全章校正计
4. **蒸馏**：通读章节 md，按 `docs/schema.md` 写卡。密度参考：已完成的 10 章平均每章 3-5 张卡。引文逐字取自章节 md（全角引号）；页码对 `<!-- page: pdf=N book=M -->` 标记核实
5. **审查+收尾**：`python scripts/validate_citations.py` 必须全绿；抽查 1-2 张卡的引文/页码/现代性标注；更新 `INDEX.md` 主索引与主题索引（新卡纳入已有主题，必要时新增主题）
6. **提交推送**：conventional commits（`feat(ingest): …` / `feat(distill): …`）+ `git push`

### 3.4 审查流程（协作约定）

采用 subagent-driven development：每个任务 = implementer 执行 + 审查（短任务可把 spec review 与 quality review 合并为一次）。审查关注：引文能否逐字定位、页码是否正确、modernity 标注是否恰当、卡片之间是否重复（跨章概念优先在主题索引关联而非重复立卡）。

## 4. P2c：产出层（P2b 完成后）

### 4.1 QMind 入库

- MCP 工具已核实：`add_source(notebookId, {kind:"text", title, content})`、`retrieve(notebookId, query, topK)`
- **限制：QMind MCP 无创建 notebook 的工具**——需用户先在 QMind UI 建好「金融经典蒸馏」notebook；执行时先 `list_notebooks` 确认，拿不到 notebookId 就找用户要
- 入库映射：**每卡一个 text source**；title = `II-<卡id> <卡H1>`（例：`II-P-01-01 投资的三要素定义`）；content = 卡全文（含 frontmatter，便于命中后直接取页码/引证/现代性）
- 入库后抽 3-5 个 `tests/question-set.md` 的问题做 retrieve 验证

### 4.2 graham-advisor skill

- 以格雷厄姆视角回答投资决策问题；回答样式已定稿（见 `docs/USAGE.md` 第 6 节四层结构），勿改样式除非用户要求
- 四子命令（计划中）：ask（问答）、check（决策对照清单）、explain（概念解释）、compare（书中观点 vs 现代转译）
- 防幻觉三条款：引文必须来自卡片；无命中明说"本书未讨论"；书中观点与现代转译显式分离
- 自知之明条款：涉及医疗/法律/具体税务等非投资专业问题时提醒用户咨询专业人士
- 详细设计见 `docs/superpowers/plans/2026-08-29-finance-distiller-p2.md` 末尾"后续阶段里程碑"

## 5. P2d：元工厂 book-distiller（最后阶段）

- 把本书管线参数化：书页偏移、章节表、schema、质量协议抽成配置，兼容扫描件与文字版两种输入
- 验收：换一本金融著作跑通端到端（选书由用户定）
- 产出形式：`book-distiller` skill（writing-skills 规范）

## 6. 铁律与环境坑（踩过的，勿重踩）

**铁律**
- 引证行格式 `**原文引证**（书页 p.N）："…"`，全角引号、逐字引自章节 md——校验器只认这个格式
- PDF 页 = 书页 + 18；卡内一律用**书页**页码
- 无引证不立卡；页码对章节 md 内嵌的 page marker 核实后再写

**环境坑**
- Windows 控制台 cp950：`pytest.ini` 等配置文件保持 ASCII，中文描述会导致解码失败
- 文件行尾：仓库配了 `.gitattributes`（eol=lf），但校验器已兼容 CRLF（读取后归一化），勿回退
- `scratch/` 目录整体 gitignore（PDF 与渲染图不入库）
- 本机可能无 git 身份：提交用 `git -c user.name="user" -c user.email="user@local" commit -m "…"`
- `gh` CLI 未安装；GitHub 操作走普通 `git push`（凭据已存，2026-08-31 验证可用）
- Bash 审批可能间歇报 "classifier unavailable"——根因是用户的审批设置，提示用户检查设置；期间用 Read/Write/Grep 做非 shell 工作，commit 由 controller 代提交
- 用户沟通偏好：**中文、通俗解释、短任务逐个做（不做长任务马拉松）、自主执行少问、定稿前先实证核实**

## 7. 待用户决定的事项

1. GitHub 仓库是否改私有（约 2026-09-02 起主动提醒一次）
2. P2b 各批次章节划分（3.2 是建议值）
3. P2d 换书验证的书目

## 8. 完成定义（DoD）

- P2b：20 章正文 + 导言/后记/附录全部有卡；`validate_citations.py` 与 `pytest` 全绿；INDEX 主索引与主题索引覆盖全部卡；每章在 `docs/p1-notes.md` 有校正记录
- P2c：QMind notebook 内可检索到全部卡；graham-advisor 四子命令可用且样式符合定稿
- P2d：book-distiller skill 在新书上端到端跑通
