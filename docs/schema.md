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

**现代转译**：<modernity=needs-translation 时必填；其余可省略>

**现代性说明**：<timeless 可一句；era-bound/needs-translation 必填>

**常见误读**：<可选>

## 模型卡（models/）

# <模型名，如 市场先生>

**定义**：<…>

**原文引证**（书页 p.<N>）：“<…>”

**现代转译**：<modernity=needs-translation 时必填；其余可省略>

**适用场景**：<…>

**常见误用**：<…>

## 检查清单卡（checklists/）

# <清单名，如 投资vs投机自检>

**用途**：<…>

**条目**：
- [ ] <条目 1>（依据 p.<N>）
- [ ] <条目 2>（依据 p.<N>）

**原文引证**（书页 p.<N>）：“<…>”

**现代转译**：<modernity=needs-translation 时必填；其余可省略>

## 框架卡（frameworks/）

# <框架名，如 安全边际估值三步>

**步骤**：1. … 2. …（每步附依据页）

**原文引证**（书页 p.<N>）：“<…>”

**现代转译**：<modernity=needs-translation 时必填；其余可省略>

**时代受限项**：<列出依赖时代数据的步骤及转译>

## 铁律
无引证不立卡：每张卡至少一条 **原文引证**，引文必须能在对应章节 md 中逐字（忽略空白）定位。
