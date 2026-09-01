# mathmodel-skill — 数学建模三竞赛统一工作流

> 三合一数学建模 Skill：覆盖 **选题 → 建模 → 求解 → 稳健 → 写作 → 终审 → 提交合规** 全链路与全工具。

[![License](https://img.shields.io/badge/license-MIT-22c55e)](./LICENSE)
[![Competitions](https://img.shields.io/badge/CUMCM%20%7C%20MCM%2FICM%20%7C%20Diangong-workflow-f97316)](./competitions/)

---

## 为什么需要它

数学建模比赛很少因为“缺少一个更聪明的回答”而失败。更常见的是：模型换了摘要没更新、第二问重解后第三问仍引用旧结果、关键假设只存在于聊天记录里、临近提交才发现匿名或 AI 披露不合规。

本 Skill 用一份共享状态（`decision_log.json`）+ 确定性脚本 + 独立门禁，把 72–96 小时的竞赛协作变成**可恢复、可检查、可交接**的流程：上下文可以变化，项目结构不会消失。Codex 与 Claude Code 可在同一工作区接力，跨会话继续。

## 核心能力矩阵

| 能力 | 说明 |
|---|---|
| **10 阶段项目流程** | Stage 0 启动 → 9 终审；每阶段输入/产物/退出条件明确，可按 Qi 局部回修 |
| **三角色执行引擎** | 建模手 / 编程手 / 论文手三份角色手册，负责阶段内实际执行 |
| **5 门禁独立质检** | `M1/P1/P2/W1/W2` 在每个交付物边界派发只读 Subagent 验收，`FAIL` 必须返工 |
| **L1–L4 反馈层** | 阶段打分 → 跨阶段回检 → 独立 Panel → 证据校准（`championship` 启用 L3/L4） |
| **三竞赛包** | cumcm（91 来源/59 样本）、mcm（COMAP 2027）、diangong（官网基线）各自的规则/反模式/写作启发/评分覆盖 |
| **7 类算法资料** | 优化/预测/评价/图论/统计/综合/机器学习，含公式、参数、代码要点，与 `model_catalog.md` 双轨路由 |
| **出版级可视化** | `tools/figure`：数据剖析 → 选图 → 三类图体系（原始/过程/结果）→ 自检闭环 → SVG+PNG 导出 |
| **双引擎论文搜索** | `tools/paper_search`：OpenAlex + AnySearch 并行检索与交叉核验 |
| **LaTeX 编译 + 预检** | `scripts/render_paper.py` 主编译链路 + `scripts/latex_check/` 四类预检（环境/引用/关键词/匿名 PDF） |
| **Word 降级路径** | `tools/docx`：OMML 公式、三线表、修订批注（用户显式要求时使用） |

## 快速开始

### 安装

```bash
# 把整个 mathmodel-skill 文件夹复制到对应工具的 skills 目录
# Claude Code：~/.claude/skills/mathmodel-skill/
# Codex：~/.agents/skills/mathmodel-skill/  或  ~/.codex/skills/
```

### 使用

进入 Claude Code 后输入：

```text
开始建模
```

或显式指定：

```text
使用 mathmodel-skill 开始 CUMCM 建模
使用 mathmodel-skill 生成 MCM/ICM A 题论文项目
```

首次启动收集 5 个启动字段（竞赛 / 题号 / 队员特长 / 截止时间 / 题目 PDF 路径），自动初始化 `<cwd>/state/decision_log.json` 后进入 Stage 0。

### 工作区产物结构

```text
my-modeling-project/           # <cwd>，用户工作目录（只写）
├── state/
│   └── decision_log.json      # 决策、评分、回退、规则与 AI 使用台账（唯一状态源）
├── 题目分析报告.md            # 建模手交付物（Stage 4）
├── 术语表格.md                # 建模手交付物（Stage 4）
├── results/                   # 结构化结果 + 复现清单.json（含种子/输入SHA-256/依赖版本）
├── figures/                   # 原始/过程/结果三类图（raw_q1_* / process_q1_* / result_q1_*）
├── paper_workspace/           # 01_abstract.md … 10_appendix.md（论文手装配源）
├── paper_output/              # TeX 中间文件与最终 PDF（默认交付）
└── support_materials/         # 代码、数据清单与竞赛要求的披露材料
```

## 主流程速览

10 阶段 × 三角色 × 5 门禁：

| # | 阶段 | 角色 | 门禁 |
|---|------|------|------|
| 0 | 团队启动 + 资料预扫 | — | — |
| 1 | 选题（多题对比 → 1） | — | — |
| 2 | 问题拆解 | 建模手 | — |
| 3 | 模型选型 | 建模手 | — |
| 4 | Foundation | 建模手 | **M1** |
| 5 | 递归子问题循环 Q1..Qn | 编程手 | **P1 → P2** |
| 6 | 稳健性 / 灵敏度 | 编程手 | — |
| 7 | 模型评价 + 推广 | 建模手 | — |
| 8 | 论文装配与写作 | 论文手 | **W1 → W2** |
| 9 | 提交前终审 + Panel | 论文手 | — |

完整映射见 [`references/角色-阶段映射.md`](references/角色-阶段映射.md)；主入口协议见 [`SKILL.md`](SKILL.md)。

## LaTeX 工作流（默认交付 PDF）

```bash
# 1. 环境预检（编译前）
python scripts/latex_check/check_latex_env.py --contest cumcm --use-ref-bib

# 2. 装配 + 编译（render_paper.py 按 MATHMODEL:SECTION marker 组装 paper_workspace）
python scripts/render_paper.py --competition cumcm --workspace paper_workspace

# 3. 提交前校验
python scripts/latex_check/check_latex_refs.py main.tex --bib ref.bib
python scripts/latex_check/check_latex_keywords.py main.tex        # CUMCM
python scripts/latex_check/check_pdf.py main.pdf --identity-mode strict
```

- 中文（cumcm/diangong）固定 **XeLaTeX**；美赛 pdfLaTeX。禁止 CUMCM 用 `latexmk -pdf`。
- 可选官方类降级模板：`templates/latex-alt/cumcm/`（内置轻量 `cumcmthesis.cls` 兼容类 + `ctexart` fallback）与 `templates/latex-alt/mcm-icm/`。
- Word（`tools/docx`）为可选降级路径，仅用户显式要求时使用。

## 辅助工具

| 工具 | 用途 |
|---|---|
| `scripts/doctor.py` | 检查 skill 结构、竞赛包、环境与工作区（`--competition cumcm \| mcm \| diangong`） |
| `scripts/score_artifact.py` | 校验 critic JSON、重算加权分数与 verdict、聚合 per-Qi |
| `scripts/extract_diff.py` | 生成并应用 section-level patch |
| `scripts/render_paper.py` | 装配 paper_workspace 为三竞赛 TeX/PDF |
| `scripts/render_ai_usage.py` | 生成 CUMCM/MCM AI 使用披露材料 |
| `scripts/latex_check/*.py` | 环境 / 引用 / 关键词 / 匿名 PDF 四类预检 |

## 三竞赛差异速查

| | CUMCM | MCM/ICM | 电工杯 |
|---|---|---|---|
| 时长 / 语言 | 72h 中文 | 96h English | 72h 中文 |
| LaTeX 引擎 | xelatex / 原创 ctexart | pdflatex / article | xelatex / ctex |
| 页数 | 摘要 p1，正文 ≤30，无目录 | 主解法 ≤25（含摘要/参考文献/代码），≥12pt | 封面 p1，摘要 p2 起编号，正文 ≤25，无目录 |
| 经验数据 | 91 来源 / 59 样本（观察分位，非官方阈值） | `n=0` | `n=0` |
| AI 披露 | 已用→`AI工具使用详情.pdf`；未用→声明 | `Report on Use of AI`（主解法后） | 保持台账，逐年核对 |

规则会变化：`competitions/<comp>/current_rules.md` 保存最近核对日期与官方入口，正式提交前必须以当届官方通知为准。

## 开发与验证

```bash
python -m compileall -q scripts tools references/roles/编程手/scripts templates/shared/code_starter
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/doctor.py --competition cumcm --skip-tools
python scripts/doctor.py --competition mcm --skip-tools
python scripts/doctor.py --competition diangong --skip-tools
python scripts/latex_check/check_latex_env.py --contest cumcm
```

## 边界与可信度

- 本 Skill 是协作与质量控制工具，不保证模型正确，也不预测奖项。它让项目可恢复、可检查、可局部修改，并最终交付。
- 生成论文仅供参考；结构与格式必须符合当届官方规则，任何 AI 生成的公式、代码、事实和引用必须由团队复核。
- 经验数据只作参照（国赛观察分位 / 美赛·电工杯 n=0），不是官方评分线，也不能推导获奖概率。

## License

MIT License（详见 [LICENSE](LICENSE)）。运行时依赖与外部资料遵循各自许可（详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)）。
