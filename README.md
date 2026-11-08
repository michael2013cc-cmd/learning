# learning · 金融著作蒸馏系统

把经典金融著作（扫描件或文字版）蒸馏为**结构化、可引证、带时效标注**的知识卡片库。
这不是一份"读书笔记"，而是一套可检索、可溯源、可驱动 AI 投资顾问的知识资产。

当前成果：《聪明的投资者》（Benjamin Graham，原本第 4 版，人民邮电出版社 2011 中译本）
**全书蒸馏完成**——20 章正文 + 导言/后记/附录，共 **98 张卡片**（截至 2026-11）。

## 它解决什么问题

| 困难 | 本项目的设计回应 |
|---|---|
| 原书是 422 页**纯扫描 PDF**，无文本层，不可检索 | Ingest 层：OCR 提取 + 逐页视觉校正协议 |
| AI 总结长书会**编造引文** | 引证铁律：无引证不立卡，校验脚本保证每条引文能在原文逐字定位 |
| 1970 年代的数值**不能直接套用**到今天 | 现代性三值标注：timeless / era-bound / needs-translation |
| 读完就忘，知识**无法在决策时刻被调用** | 主题索引按真实问答场景聚合跨章卡片（17 个场景） |

## 架构：四段管线

```
源书 PDF（scratch/ii.pdf，不入库）
   │
   ▼
① Ingest 读取层    PyMuPDF 渲染 → RapidOCR 识别 → 视觉校正（逐页比对）
│                  产出 ingest/<book>/chapters/ch-NN.md（带页码标记）+ page-map.md
▼
② Distill 蒸馏层   按 schema v2 立卡（原则/模型/清单/框架）→ 引证校验器把关
│                  产出 distilled/<book>/ + INDEX.md
▼
③ Output 产出层    （规划中）QMind 知识库入库 + graham-advisor 顾问 skill
▼
④ Meta 沉淀层      （规划中）book-distiller 元 skill——管线参数化，换书复用
```

每阶段设人工质量门，不自动推进（P1 样章验证 → P2 全书推进 → P3 元工厂）。

## 目录结构

```
ingest/the-intelligent-investor/
  chapters/            # OCR 提取的章节全文（23 个文件，~15,000 行，含页码标记）
  page-map.md          # 章节 ↔ 书页 ↔ PDF 页映射（偏移：PDF 页 = 书页 + 18）
distilled/the-intelligent-investor/
  book.json            # 书目元数据
  INDEX.md             # 主索引（按卡型）+ 主题索引（17 个问答场景）★使用入口
  principles/  (62)    # 原则卡：核心论断，严格引证
  models/      (10)    # 模型卡：思维工具（市场先生、安全边际…）
  checklists/  (14)    # 清单卡：决策前逐项自查
  frameworks/  (12)    # 框架卡：完整分析流程（每步附依据页与时效标注）
scripts/
  ingest.py            # 页码换算、渲染、OCR、章节格式化
  extract_chapters.py  # 按章提取 CLI（CHAPTERS 表登记制）
  validate_citations.py# 引证铁律校验器
tests/                 # pytest + 8 题质量门测试集
docs/
  USAGE.md             # 日常操作手册（环境/命令/校正协议/回答样式）
  schema.md            # 卡片格式 v2 定义
  knowledge-usage.md   # ★知识使用指南：什么时候、什么场景、怎么用这些卡片
  p1-notes.md          # 每章视觉校正记录 + 质量审计
  superpowers/         # 设计文档、实施计划、交接 spec
```

## 卡片体系（schema v2）

| 卡型 | 前缀 | 数量 | 回答的问题 | 典型卡 |
|---|---|---|---|---|
| 原则 principle | P | 62 | "原书怎么说、为什么成立、常被怎么误读" | P-20-01 安全边际、P-08-01 波动是机会非指示 |
| 模型 model | M | 10 | "用什么思维透镜看当前处境" | M-08-01 市场先生、M-14-01 预测法 vs 保护法 |
| 清单 checklist | C | 14 | "这笔决策放行前逐项查什么" | C-20-01 买入前安全边际清单、C-01-01 投资vs投机自检 |
| 框架 framework | F | 12 | "从头到尾怎么执行一项分析" | F-20-01 安全边际估值六步、F-15-01 烟蒂股操作 |

每张卡的 frontmatter：`id / type / chapter / pages / importance(core|important|minor) / modernity`。

**三条铁律**
1. **无引证不立卡**——每卡至少一条 `**原文引证**（书页 p.N）："…"`，引文须能在对应章节 md 中逐字定位（`validate_citations.py` 自动校验）
2. **页码一律用书页**（PDF 页 = 书页 + 18，对章节内嵌 page marker 核实）
3. **现代性标注**：`era-bound` 卡的数值不可直接使用；`needs-translation` 卡必须附"现代转译"段；框架各步骤、清单各条目可再附行内时效标注

## 快速开始

```bash
# 环境：Python 3.11
pip install -r requirements.txt
# ⚠️ 版本锁定：onnxruntime==1.19.2 + numpy==1.26.4，升级会导致 rapidocr 无法启动，勿动

python -m pytest tests/ -q             # 预期：10 passed, 2 skipped（skipped 为需源书 PDF 的慢速冒烟）
python scripts/validate_citations.py   # 预期：all citations verified

# 提取新章节（需先向仓库所有者索取源书 scratch/ii.pdf，已 gitignore）
# 1) 在 scripts/extract_chapters.py 的 CHAPTERS 表登记 ("ch-NN", 标题, PDF页起, PDF页止)
python -m scripts.extract_chapters ch-NN
```

蒸馏新章节的标准六步流程（登记 → 提取 → 视觉校正 → 蒸馏 → 审查收尾 → 提交）见
[docs/USAGE.md](docs/USAGE.md) 与交接 spec：`docs/superpowers/specs/2026-09-01-handover-remaining-work.md`。

## 如何使用这些知识

**入口是 [`distilled/the-intelligent-investor/INDEX.md`](distilled/the-intelligent-investor/INDEX.md)**：

- 按问题查 → 主题索引（17 个场景，如"面对市场波动的态度""买入决策与安全边际"）→ 定位卡 id → 读卡正文 → 带书页页码回答
- 按书读 → 主索引按卡型分节通读

什么时候用哪类卡、典型决策场景的卡片组合、使用红线（modernity 过滤、"本书未讨论"边界），
详见 **[docs/knowledge-usage.md](docs/knowledge-usage.md)**。

产出层规划：卡片入库 QMind 知识库（每卡一文档）+ `graham-advisor` skill，
以格雷厄姆视角按固定四层结构回答（清单对照 → 逐条引证 → 书中观点/现代转译分离 → 明确结论）。

## 状态与路线图

- [x] P1 样章验证（第 1/8/20 章手工深蒸馏，schema 定稿，8 题测试集通过）
- [x] P2b 全书蒸馏（20 章 + 导言/后记/附录，98 卡，引证校验全绿）
- [ ] P2c 产出层：QMind 入库 + `graham-advisor` skill（回答样式已定稿，代码未写）
- [ ] P2d/P3 元工厂：`book-distiller` 元 skill（换一本书端到端验证泛化）

## 提交约定

Conventional commits：`feat(ingest): …`、`feat(distill): …`、`fix: …`、`docs: …`。

## 版权与免责说明

- 源书 PDF 因版权**不随仓库分发**（`scratch/` 整体 gitignore）；卡片中的中文引文引自
  人民邮电出版社 2011 年版《聪明的投资者》（王中华、黄一义译），仅作个人学习研究之用。
- 本项目是知识整理工程，不构成投资建议；卡片含大量 1960-70 年代美国市场数值，
  使用前务必阅读卡内"现代性说明/现代转译"。
