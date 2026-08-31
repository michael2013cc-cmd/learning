# 用法说明（最新版，2026-09-01）

> 本仓库是"金融著作蒸馏系统"，当前正在蒸馏《聪明的投资者》（人邮 2011 中译本，原本第 4 版）。
> 相关文档：卡片格式 `docs/schema.md`；设计与路线 `docs/superpowers/specs/`；进度与质量审计 `docs/p1-notes.md`；接手指南 `docs/superpowers/specs/2026-09-01-handover-remaining-work.md`。

## 1. 环境准备

- Python 3.11，安装依赖：`pip install -r requirements.txt`
- 关键版本锁定：`onnxruntime==1.19.2` + `numpy==1.26.4`（升级会导致 rapidocr 无法启动，勿动）
- 源书 `scratch/ii.pdf`（422 页扫描件）**不在 git 仓库内**（已 gitignore），需本地放置
- 页码映射铁律：**PDF 页 = 书页 + 18**；全书对照表见 `ingest/the-intelligent-investor/page-map.md`

## 2. 常用命令

| 目的 | 命令 | 期望输出 |
|---|---|---|
| 提取章节（OCR） | `python -m scripts.extract_chapters ch-NN` | 生成 `ingest/the-intelligent-investor/chapters/ch-NN.md` |
| 引证校验 | `python scripts/validate_citations.py` | `all citations verified` |
| 测试 | `python -m pytest tests/ -q` | 12 passed（含一个需要 `scratch/ii.pdf` 的 slow 冒烟） |

提取新章节前，先在 `scripts/extract_chapters.py` 的 `CHAPTERS` 表登记：
`("ch-NN", "章节标题", PDF页起, PDF页止)`。运行时若 stderr 出现 `WARN low-char page N`，表示该页疑似 OCR 失败，抽检时重点关注。

## 3. 视觉校正协议（每章必做）

rapidocr 在约 18% 的页面会整句缺失，因此每章蒸馏前必须：

1. 抽 2 页渲染成 PNG，用 Read 工具与 `ch-NN.md` 逐字比对
2. 通过标准：**单页错字 ≤ 3 且无整句缺失**
3. 不通过（实测几乎每章都不通过）→ 全章逐页视觉校正，并在 `docs/p1-notes.md` 追加校正记录小节

高频形近错字表（校正时优先检查）：自已→自己、买人→买入、投人→投入、收人→收入、进人→进入、纳人→纳入、归答→归咎、深人→深入；破折号统一为"——"。

## 4. 蒸馏卡片（schema v2）

- 四类卡：principles（P）/ models（M）/ checklists（C）/ frameworks（F），文件名 `<类型>-<章号两位>-<序号两位>.md`
- **铁律：无引证不立卡**——每张卡至少一条引证，格式固定为
  `**原文引证**（书页 p.N）："…"`（全角引号；引文必须能在章节 md 中逐字定位，空白由校验器归一化）
- modernity 三值：`timeless`（跨时代）/ `era-bound`（数值依赖 1960-70 年代）/ `needs-translation`（须附"现代转译"段）；frameworks 各步骤、checklists 各条目可再附行内步骤级标注
- checklist 卡含 **正向案例** 字段；frameworks 卡含 **时代受限项** 字段
- 完整格式与字段定义见 `docs/schema.md`；成卡样例见 `distilled/the-intelligent-investor/`

## 5. 索引与检索

- `distilled/the-intelligent-investor/INDEX.md`：主索引（按卡型分节，含章号/页码/现代性/重要性）+ 主题索引（9 个问答场景聚合跨章卡）
- 使用路径：按问题场景查主题索引 → 定位卡 id → 读卡正文 → 带书页页码回答

## 6. 格雷厄姆顾问回答样式（原型已定稿）

以格雷厄姆视角回答投资决策问题时，固定四层结构：

1. **清单对照**：用相关 checklist 卡逐条对照用户决策，打 ✅/❌
2. **逐条引证**：每条判断附"原文引证"及书页页码
3. **书中观点 / 现代转译** 两节显式分离，不混杂
4. **明确结论**：直说格雷厄姆会怎么判断，不含糊

书中未覆盖的话题，明说"本书未讨论"，不得编造引文。

## 7. 提交约定

- Conventional commits：`feat(ingest): …`、`feat(distill): …`、`fix: …`、`docs: …`
- 本机若无 git 身份配置，用 `git -c user.name="user" -c user.email="user@local" commit -m "…"`
- 远端：`https://github.com/michael2013cc-cmd/learning`（截至 2026-09-01 为公开仓库；用户计划改私有，执行前先确认）
