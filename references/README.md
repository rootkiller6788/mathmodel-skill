# references/ 通用层索引

本目录承载竞赛无关的**流程与质量通用层**；竞赛特化内容在 `competitions/<comp>/`。按 SKILL.md 的懒加载协议，只在实际进入对应阶段时才读取相关文件，**不要一次性全量加载**。

## 10 阶段时间线

| 文件 | 阶段 | 承担角色 | 门禁 | 关键产物 |
|---|---|---|---|---|
| `stage_00_kickoff.md` | 0 启动 + 资料预扫 | — | — | 启动字段、环境、规则基线 |
| `stage_01_problem_selection.md` | 1 选题 | — | — | 选择理由、放弃项、task_type |
| `stage_02_analysis.md` | 2 问题拆解 | 建模手 | — | 子问、变量、约束、依赖图 |
| `stage_03_model_selection.md` | 3 模型选型 | 建模手 | — | 候选模型、证据、淘汰理由 |
| `stage_04_foundation.md` | 4 Foundation | 建模手 | **M1** | `题目分析报告.md` + `术语表格.md` |
| `stage_05_subproblem_loop.md` | 5 递归子问题 Q1..Qn | 编程手 | **P1 → P2** | 代码、results、figures、复现清单 |
| `stage_06_robustness.md` | 6 稳健性/灵敏度 | 编程手 | — | 稳健区间、失败边界 |
| `stage_07_evaluation.md` | 7 模型评价+推广 | 建模手 | — | 优缺点、改进、迁移条件 |
| `stage_08_writing.md` | 8 论文装配与写作 | 论文手 | **W1 → W2** | paper_workspace → LaTeX/PDF |
| `stage_09_review.md` | 9 提交前终审 | 论文手 | — | 最终 PDF、Panel 记录 |

## 三角色执行引擎

`roles/<建模手|编程手|论文手>/SKILL.md` 是阶段内的执行手册；各角色下另有自己的 `references/`（工作流、质检清单、写作/LaTeX 规范等）与 `scripts/`（如编程手的出图/复现脚本）。角色与阶段的映射见 [`角色-阶段映射.md`](./角色-阶段映射.md)，调度协议见 [`Subagent调度.md`](./Subagent调度.md)。

## 反馈层与评分

| 文件 | 作用 |
|---|---|
| `feedback_layer1_critic.md` | L1 每阶段轻量打分（critic schema） |
| `feedback_layer2_backtrack.md` | L2 跨阶段回检，触发定向回滚 |
| `feedback_layer3_panel.md` | L3 独立 Panel（championship） |
| `feedback_layer4_calibration.md` | L4 证据校准 |
| `rubrics.md` | 维度 rubrics；与 `feedback_layer1_critic.md`、`scripts/score_artifact.py` 的定义必须一致 |

## 建模选型资料

- `model_catalog.md`：候选模型目录，跨竞赛复用。
- `算法索引.md`：把 7 类算法（`assets/`）与模型目录双轨路由；按需深挖对应 `assets/0N-*.md`。
- `harness_compat.md`：运行环境兼容说明。

## 离线语料

`papers/`：官网展廊 PDF 的下载/重建说明（`README.md`、`_DOWNLOAD_REPORT.md`）。仓库不跟踪 PDF，见根 `.gitignore`。

## 维护约定

- 改任一阶段流程或角色手册时，同步更新本索引、`../SKILL.md` 对应表格与根 `README.md`。
- 规则、评分或状态 schema 有变时，遵循根 `AGENTS.md` 的联动更新要求。
