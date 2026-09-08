---
name: mathmodel-skill
description: CUMCM 国赛、MCM/ICM 美赛与电工杯数学建模竞赛的端到端协作工作流，以及一般数学建模项目。Use when a user works on a modeling competition (cumcm/mcm/icm/diangong/国赛/美赛/电工杯) or asks to run/review a modeling-competition paper from problem selection through modeling, solving, robustness, writing, compliance, and final submission review. 采用 10 阶段项目流程为脊柱、建模手/编程手/论文手三角色为阶段内执行引擎、5 个独立门禁质检，并集成双引擎论文搜索、出版级可视化、LaTeX/PDF 编译与预检、Excel/PDF 等工具。Do not trigger for generic model selection, ordinary data analysis, or non-competition paper review.
---

# mathmodel-skill — 数学建模三竞赛工作流（10 阶段 × 三角色 × 5 门禁）

本 Skill 把 72–96 小时的竞赛协作组织为可恢复、可检查、可交接的流程：**10 阶段项目时间线**（选题→拆题→建模→求解→稳健→写作→终审）为脊柱，**建模手 / 编程手 / 论文手**三角色负责阶段内的实际执行，**5 个独立门禁质检**（`M1/P1/P2/W1/W2`）在每个交付物边界验收，L1–L4 反馈层驱动打分与定向精修。用户回答关键问题，agent 维护状态与脚本。

- **10 阶段**：`references/stage_00..09_*.md`；状态统一存 `<cwd>/state/decision_log.json`。
- **三角色**：`references/roles/{建模手,编程手,论文手}/SKILL.md`，映射见 `references/角色-阶段映射.md`。
- **5 门禁**：`references/Subagent调度.md` 定义固定质检协议。
- **全工具**：`tools/{figure,paper_search,docx,xlsx,pdf,latex}` + `scripts/latex_check/` 预检。
- **生成论文仅供用户参考**，非可直接提交作品；结构格式以当届官方规则为准。

**使用前**：把 `使用指南.md` 复制到工作区 `<cwd>/`。

## 强制执行协议

用户点名本 Skill 或任务命中时，严格执行，不降级为建议：

1. 首次进度更新中回显：已激活本 Skill、`<cwd>`、当前阶段、目标竞赛与届次、计划读取的角色和工具入口。未确认的官方规则标为待核验。
2. 进入每个阶段前**实际读取**该阶段角色 `SKILL.md`；使用 PDF、Excel、论文搜索、DOCX 或 LaTeX 时再读取对应工具 `SKILL.md`。知道路径 ≠ 已执行。
3. 严格调用本 Skill 提供的脚本和模板；已有初始化、转换、编译或校验工具时，禁止手写替代实现。
4. 任何校验预警视为未完成；只有当届官方规则或用户明确要求允许偏离时，记录“规则来源、偏离项、理由”后继续。
5. 环境缺少引擎、搜索源或依赖时，报告阻塞并继续完成仍可验证的部分；禁止静默换工具或用较差产物冒充完成。
6. 按 `references/Subagent调度.md` 在 `M1/P1/P2/W1/W2` 节点立即派发独立质检，禁止等全流程结束后才首次派发；作者自检不能替代独立验收。除固定质检外不主动派发其他 Subagent。
7. 交付前运行当前阶段的全部完成门禁；任一命令未运行、退出码非零、门禁未通过时，不得声称“已完成”。
8. 最终回复列出实际读取的入口、实际运行的关键命令与退出码、门禁状态、核心质量指标和仍存在的阻塞；不得只说“已检查”。

## 三竞赛 × 三模式矩阵

| Competition | 时长 | 语言 | LaTeX 引擎 | 规则基线 | 经验数据 |
|---|---|---|---|---|---|
| cumcm | 72h | 中文 | xelatex / 原创 ctexart | CUMCM 2026 | 91 来源 / 59 可提取样本 |
| mcm | 96h | English | pdflatex / article | COMAP 2027 | `n=0`，无论文分位 |
| diangong | 72h | 中文 | xelatex / ctex | 官网 2026-03-21 | `n=0`，无论文分位 |

| Mode | 反馈层 | 用途 |
|---|---|---|
| fast | L1 单次 | 选题试跑 / sanity check |
| standard | L1 + L2 | 默认主流程 |
| championship | L1+L2+L3+L4 + red-team | 终稿前深度评审 |

模式按距 deadline 自动推荐（>60h standard；<6h 直进 Stage 9 championship）。

## 10 阶段索引

| # | 阶段 | 承担角色 | 门禁 | 时长 | 关键产物 |
|---|------|---------|------|------|---------|
| 0 | 团队启动 + 资料预扫 | — | — | 1h | 启动字段、环境、规则基线 |
| 1 | 选题（多题对比 → 1） | — | — | 2-4h | 选择理由、放弃项、task_type |
| 2 | 问题拆解 | 建模手 | — | 2-3h | 子问、变量、约束、依赖图 |
| 3 | 模型选型 | 建模手 | — | 2-4h | 候选模型、证据、淘汰理由 |
| 4 | Foundation | 建模手 | **M1** | 1h | `题目分析报告.md` + `术语表格.md` |
| 5 | 递归子问题循环 Q1..Qn | 编程手 | **P1 → P2** | 按题分配 | 代码、`results/`、`figures/`、`复现清单.json` |
| 6 | 稳健性 / 灵敏度 | 编程手 | — | 2-3h | 稳健区间、失败边界 |
| 7 | 模型评价 + 推广 | 建模手 | — | 1-2h | 优缺点、改进、迁移条件 |
| 8 | 论文装配与写作 | 论文手 | **W1 → W2** | 12-30h | `paper_workspace/*.md` → LaTeX/PDF |
| 9 | 提交前终审 + Panel | 论文手 | — | 2-6h | 最终 PDF、支持材料、Panel 记录 |

## 角色路由（三角色执行引擎）

| 阶段 | 加载入口 | 固定交付物 |
|---|---|---|
| 2/3/4/7 | `references/roles/建模手/SKILL.md` | `题目分析报告.md`、`术语表格.md` |
| 5/6 | `references/roles/编程手/SKILL.md` | `.py/.m` 代码、`results/` 表格、`figures/`（原始/过程/结果三类，每类≥3张且覆盖全部子问题）、`results/复现清单.json` |
| 8/9 | `references/roles/论文手/SKILL.md` | 默认 LaTeX/PDF（`完整论文-LaTeX/` + `完整论文.pdf`）；用户显式要求时 Word（`完整论文.docx`） |

默认至少 8 幅正式图且覆盖全部子问题；当届官方规则或用户要求冲突时以官方为准并记录依据。

## 5 门禁映射

L1 每阶段轻量打分，L2 跨阶段回检，L3 独立 Panel，L4 证据校准；**5 门禁为交付物边界的独立 Subagent 验收**（默认开启）：

| 门禁 | 触发点 | 验收物 |
|---|---|---|
| `M1` 建模终检 | Stage 4 结束 | 题目分析报告 + 术语表格 |
| `P1` 最小可运行 | Stage 5 首个 Qi 切片 | 最小可运行结果（纵向切片） |
| `P2` 编程终检 | Stage 5 结束 | 代码 + 三类图 + 复现清单 |
| `W1` 证据大纲 | Stage 8 写正文前 | 主张—证据映射 + 大纲 |
| `W2` 论文终检 | Stage 8 结束 | 完整论文（LaTeX/PDF 或 Word） |

门禁回执含 6 字段（范围/输入快照/状态/证据/发现 P0-P1-P2/返工）；`FAIL` 不可被主 Agent 改写。完整协议见 `references/Subagent调度.md`。

## 加载协议（节省 token 的关键）

只在进入阶段 N 时加载 `references/stage_NN_*.md`，**切勿**一次性全读。各阶段额外加载：

- 每阶段开头/结尾：`<cwd>/state/decision_log.json` 必读/必写。
- Stage 1：`competitions/<comp>/topic_specs.json`；Stage 3/5：`references/model_catalog.md`（候选生成）再按 `references/算法索引.md` 读对应 `assets/*.md`（算法实现深挖）。
- Stage 0/8/9：`competitions/<comp>/current_rules.md` 并核对官方链接。
- Stage 8：`competitions/<comp>/{winning_patterns,phrase_bank,abstract_template,paper_skeleton}.md` + cumcm 的 `style_guide.md`；经验锚点 `empirical.json` 只作参考。
- Stage 9：`anti_patterns.md` + `rubric_overlay.json` panel personas。
- 工具：PDF→`tools/pdf`，Excel→`tools/xlsx`，搜索→`tools/paper_search`，画图→`tools/figure`，LaTeX 编译→`tools/latex` + `scripts/latex_check/`，Word→`tools/docx`。

## 收敛准则（verdict 优先级）

`block`（≥1 high-severity）→ `pass_early`（raw_min≥9 且 weighted_mean≥9）→ `pass`（raw_min≥7 且 weighted_mean≥8）→ `pass_with_review`（Stage5 任一 Qi mark_for_review）→ `refine` → `refine_partial`（仅失败 Qi）→ `carryover`（iter≥3）。

`weighted_mean = Σ(sᵢwᵢ)/Σwᵢ`，权重来自 `config/dim_weights.json[<comp>][<task_type>]`（clamp [0.7,1.5]）。此定义在 `feedback_layer1_critic.md` / `rubrics.md` / `scripts/score_artifact.py` 三处必须一致。

## 状态持久化

- 状态源：`<cwd>/state/decision_log.json`（v3.1），Codex 与 Claude Code 互通；跨会话接力。
- 每阶段开头读 `current_stage` 决定恢复点，结尾写核心决策 + 5 维评分，`current_stage += 1`。
- Stage 5 保存 per-Qi 状态，支持 `refine_partial` / `pass_with_review`。
- L2 跨阶段回检读此文件主动找冲突，触发定向回滚（不重做整阶段）。
- 环境变量：`MATHMODEL_STATE_DIR` / `MATHMODEL_COMPETITION` 可覆盖。

## LaTeX 策略

- **主编译链路**：`scripts/render_paper.py` 把 `paper_workspace/*.md` 按 `MATHMODEL:SECTION` marker 装配进 `templates/latex/<comp>/main.tex`（fail-closed，占位符/缺失章节直接失败），再编译 PDF。
- **引擎分派**：中文（cumcm/diangong）固定 **XeLaTeX**；美赛 pdfLaTeX。**禁止** CUMCM 用 `latexmk -pdf`（会强制 pdfLaTeX）。
- **编译前预检**：`python scripts/latex_check/check_latex_env.py --contest <comp> [--use-ref-bib] [--strict-class]`。
- **提交前校验**：
  - `scripts/latex_check/check_latex_refs.py main.tex --bib ref.bib`（`\cite`/`\ref` 完整性）
  - CUMCM：`scripts/latex_check/check_latex_keywords.py main.tex`（关键词须为建模术语）
  - `scripts/latex_check/check_pdf.py main.pdf [--max-pages N --max-size-mb M] --identity-mode strict`（页数/大小/匿名）
- **可选官方类降级**：`templates/latex-alt/cumcm/`（内置轻量 `cumcmthesis.cls` 兼容类 + `ctexart` fallback）与 `templates/latex-alt/mcm-icm/`，非默认。
- **默认 LaTeX + PDF**；用户显式要求 Word 时走 `tools/docx` 降级路径。
- 主树 `templates/latex/<comp>/main.tex` 是 `render_paper.py` 的**唯一**装配源；`tools/latex/assets/templates/` 与 `templates/latex-alt/` 分别是子工具镜像与降级类，改动主树模板时须同步镜像或在提交中说明原因（有 `tests/test_mirror_parity.py` 守护）。

## 根目录契约与完成判定

- `SKILL_ROOT`（本文件所在目录）只读；`<cwd>`（用户工作目录）只写，所有产物只能写在这里；两个根目录必须不同。
- 声称完整完成时：当前任务涉及的独立门禁均为 `PASS` 且通过后产物未发生未经复验的实质变化；所有计算结论来自实际运行结果；公式/表格/图表与代码一致；引用可追溯；已按当届官方规则配置并运行对应 check 脚本；所有产物位于 `<cwd>`，`SKILL_ROOT` 未被改写。
- 环境无 Subagent 能力时，只能报告 `BLOCKED` 或受限交付，不得把主 Agent 自检描述为独立通过。

## 用户指令快捷

- “进入/重做 stage N”“切到 mcm/cumcm/diangong”“升级到 championship”“切到 fast”“回退到 stage M”“做 L2 回检”“看进度”。

## 数据来源声明

- `competitions/cumcm/`：91 份来源文档、59 份成功提取文本进入观察分位；不是官方阈值。
- `competitions/mcm/`、`diangong/`：规则基线已按官方核对；经验模式为维护者启发，`empirical.json` 为 `n=0`，不得推断数值门槛。
- 规则会变化：`current_rules.md` 保存最近核对日期与官方入口，正式提交前必须以当届官方通知为准。

## 与外部资源的关系

核心工作流可离线运行。人工补充：国赛 `personqianduixue/Math_Model`、`datawhalechina/intro-mathmodel`、dxs.moe.gov.cn 优秀论文展廊；美赛 COMAP 官网与 MCM Tutorial；电工杯中国电机工程学会论文集。
