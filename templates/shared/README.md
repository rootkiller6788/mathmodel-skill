# templates/shared/ 通用模板

主渲染用竞赛模板在 `templates/latex/<comp>/main.tex`；本目录放**项目级共享模板**，在初始化用户工作区时作为起始内容复制/参考，不直接参与 LaTeX 装配。

## 状态与台账模板

| 文件 | 用途 |
|---|---|
| `decision_log.json` | 唯一状态源的**规范模板**（schema v3.1）：`competition`/`task_type`/`problem`/`current_stage`/`compliance`/`stages`/`scores` 等。工作流每阶段读写用户项目 `state/decision_log.json`。 |
| `ai_usage_ledger.json` | AI 使用台账条目模板（schema 1.1）。把 `compliance` 节并入 decision_log；逐条按时间追加，字段含 `tool`/`model`/`use_stage`/`query`/`output`/`human_review` 等。显式空数组表示「未使用 AI」。 |

## 论文表格模板（markdown 段，论文手阶段使用）

| 文件 | 用途 |
|---|---|
| `assumption_table.md` | 假设汇总三线表骨架（编号/假设/依据/影响）。 |
| `notation_table.md` | 术语符号表骨架（符号/含义/单位），配合建模手 `术语表格.md` 保持全文一致。 |
| `sensitivity_table.md` | 灵敏度/稳健性结果表骨架。 |

## code_starter/ — 求解代码起始模板

五类问题各有起点脚本，对应论文 §5.x 的常用解法，供编程手在 Stage 5 选用改写：

| 文件 | 适用 |
|---|---|
| `classification.py` | 二分类/多分类/不平衡数据 |
| `evaluation.py` | AHP/熵权/TOPSIS/模糊综合评价 |
| `optimization.py` | LP/IP(MILP)/QP/凸优化 |
| `prediction.py` | 回归/ARIMA/GM(1,1)/LSTM/组合预测 |
| `simulation.py` | 蒙特卡罗/LHS/ODE/Agent-based（含 §6 灵敏度） |

有回归测试覆盖这些起始模板能独立运行（`tests/test_code_starters.py`），改动时保持测试通过。

## 运行时示例依赖

`requirements.txt`：**可选的完整 Python 依赖清单**（按实际所用模型安装，核心工作流无需全量安装），仅供参赛队伍参考；它不等同于根 `requirements-dev.txt`（维护者测试/预检依赖）。
