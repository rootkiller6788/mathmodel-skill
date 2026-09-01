# 编程手工作流程

## 一、读取输入

从 `PROJECT_ROOT` 读取题目附件、`题目分析报告.md` 和 `术语表格.md`。输入文件只读；输出写入新文件。

## 二、选择语言并动态检查依赖

根据用户要求、现有代码和模型函数选择 Python、MATLAB 或两者。只检查实际选中的功能。

Python：

```powershell
python ../scripts/check_env.py --features data visualization optimization
```

可选功能包括 `data`、`visualization`、`excel`、`optimization`、`integer-optimization`、`statistics`、`machine-learning`、`time-series`、`graph` 和 `image`。

MATLAB：

```matlab
addpath("../scripts");
report = check_matlab_env(["data", "visualization", "optimization"]);
assert(report.ok, "缺少所选模型需要的 MATLAB 工具箱");
```

缺少依赖时报告精确名称，不自动改用另一个模型或语言。

## 三、实现与运行

1. 把数据读取、预处理、模型、验证、可视化和输出拆成清晰函数。
2. 随机算法显式设置种子。
3. 所有关键参数集中定义并写入复现清单。
4. 实际运行代码；禁止手写或伪造结果。
5. 检查约束可行性、数值范围、边界条件和验证指标。
6. 若模型本身矛盾，把实际报错和最小复现反馈给建模手。

### 求解稳健性（跨竞赛通用）

求解稳健性贯穿各类竞赛（CUMCM / MCM-ICM / APMCM 等）与各类赛题（机理题、数据题、优化题、仿真题）。实现与运行阶段必须按以下顺序排查，作为正式出图和全量计算的前置：

1. **数值稳定性写法**
   - 概率连乘、指数和优先用 log-sum-exp（`scipy.special.logsumexp`），避免上溢；softmax 损失直接用其 log 形式。
   - 阶乘/组合数用 `math.lgamma` 或 `scipy.special.gammaln` 在对数域计算，涉及伽马/贝塔函数时同理。
   - 长尾分布、幂次计算先取对数再运算；若最终结果仅作比较或取 log，则保留对数结果不再还原。
2. **无量纲化与归一化**
   - 目标函数或约束中量纲差异超过 10³ 时，先对变量做 min-max 或 z-score 归一化再求解；物理题先做量纲一致性检查（各量纲单位对齐后再建模），数据题先做特征尺度检查。
   - 横跨多数量级的变量（如 10⁻³~10⁶）取 `log` 或 `log1p` 后建模（对数量纲）。
   - 归一化参数（均值、标准差、min/max）必须与模型一起记录，预测阶段用同一套参数还原。
3. **矩阵病态检查**
   - 求解线性系统或求逆前，计算条件数 `np.linalg.cond`；条件数 > 10⁷ 视为病态，改用 `np.linalg.lstsq`、`pinv` 或加正则化（岭回归/Tikhonov）。
   - 特征分解/幂法前检查矩阵对称性，对称矩阵用 `np.linalg.eigh`；非正定协方差用 `pinv` 或加对角扰动。
4. **优化器选型与尺度对齐**
   - 决策变量尺度差异大时，先做尺度变换（把变量缩放到同一量级）再求解，恢复时反变换。
   - 多目标/加权目标中，各目标先归一化再加权，避免量纲主导。
   - 求解器选型：线性/整数规划用 `scipy.optimize.linprog`、`pulp` 或 `ortools`；非线性连续用 `scipy.optimize.minimize`（显式传 `bounds`，尝试多种 `method`）；大规模组合优化用精确求解器或启发式（遗传/模拟退火/粒子群）对比。
   - **超时与降级**：预估求解时间，超时（如单次 > 10 分钟）主动降级——精确解→启发式、全局→局部、全量→抽样，并如实记录降级发生在复现清单中，不让模型挂死拖垮全流程。
5. **随机性与多初始值**
   - 随机算法（遗传/模拟退火/PSO/蒙特卡洛/随机森林等）显式设种子，保证可复现。
   - 非凸优化/启发式算法从多个初始值或多种子运行，报告最优解与最优值分布，避免把局部最优当全局最优。
6. **误差与收敛控制**
   - 迭代法（梯度下降、EM、幂法、求解器迭代）检查是否收敛：设置 `tol`/`max_iter`，记录迭代数与收敛标志。
   - 结果保留有效位数，与题目/论文要求一致；统计量与置信区间由代码计算，不硬编码。
7. **数据规模与计算资源边界**
   - 大规模数据（>10⁶ 行）检查内存与运行时可接受，必要时分块处理（`chunksize`）、向量化或抽样，并记录规模与处理方式。
   - KNN/SVM 等在预测阶段随数据规模变慢的算法，提前评估是否换用可扩展方法。
8. **结果 sanity check**
   - 求解后立即做量纲与数量级检查（如结果 -10⁹ 但题目问百分比 → 必有误）。
   - 边界 case 验证：输入全零→输出应为零、极端参数下模型仍返回有限值；对比一个已知简单情形验证逻辑正确。
   - 数值不稳定时记录具体现象（溢出 warning、NaN、inf）和触发条件，返回编程手排查或反馈建模手调整模型。
9. **跨平台可复现**
   - 种子、依赖版本、平台信息写入复现清单；浮点结果跨平台可能有微小差异，论文数值以唯一复现命令所在平台为准。

## 四、P1 最小可运行结果

完成数据读取、预处理和核心求解纵向切片后，在全量运行与正式出图前派发独立质检 Subagent：

1. 从 `PROJECT_ROOT` 执行一条最小命令。
2. 每个会驱动后续全量计算的模型族至少覆盖一个真实输入或结构等价小实例。
3. 核对退出码、输入到结果的追溯、单位、数值范围、关键约束和 `M1` 模型合同。
4. 实现问题返回编程手；公式、约束或参数合同问题携命令、堆栈和预期—实际证据返回建模手。

`P1` 未返回 `PASS` 不得继续全量计算、参数扫描和正式出图。它不要求三类图、完整敏感性分析或最终性能。

## 五、可视化执行链

按 `tools/figure/SKILL.md` 执行完整可视化流程（数据剖析→图表契约→选图→绘制→自检→导出），
数学建模场景额外满足以下要求：

1. 从题目分析报告提取全部子问题并规范为 `q1…qN`。
2. 每张候选图明确对应子问题、核心结论、所属类别（raw / process / result）、证据映射、统计口径和最终尺寸。
3. 三类图体系：按 `raw_q1_*`、`process_q1_*`、`result_q1_*` 等命名，每类至少 3 张、合计至少 9 张，且每个子问题在三类中各至少 1 张；每张同时导出 SVG 与 300 DPI PNG，不设上限。
4. 将 `ROLE_ROOT/scripts/plot_style.py` 或 MATLAB 出版绘图工具复制到 `PROJECT_ROOT/utils/` 后使用。
5. 所有正式图经 `tools/figure/scripts/export_figure.py` 导出后，运行 `python "<SKILL_ROOT>/references/roles/编程手/scripts/figure_audit.py" "<PROJECT_ROOT>/figures" --questions q1 q2 ... qN --strict`，实际打开 PNG 进行视觉检查；发现问题回到源代码修正并重新运行。

## 六、文件结构

```text
PROJECT_ROOT/
├── data/                         # 输入，只读
├── 题目分析报告.md               # 建模手产物，只读
├── 术语表格.md                   # 建模手产物，只读
├── 问题1_求解.py 或 问题1_求解.m
├── results/
│   ├── 问题1_结果.csv
│   ├── 题目指定结果.xlsx         # 仅题目要求或需保留模板时
│   └── 复现清单.json
└── figures/
    ├── raw_q1_*.svg / raw_q1_*.png         # 问题一原始数据图
    ├── process_q1_*.svg / process_q1_*.png # 问题一模型运行过程图
    ├── result_q1_*.svg / result_q1_*.png   # 问题一最终结果图
    ├── raw_q2_* / process_q2_* / result_q2_*  # 其余问题依次覆盖
    └── 图表面板.html
```

同一图的 SVG、PNG 和灰度预览按 1 张逻辑图计数。图可以继续多生成候选版本；每张图仍须数据正确、标题和坐标含义清楚。

## 七、Excel

- 普通结果表优先 CSV。
- 题目要求 `.xlsx`、多工作表、公式或既有模板时使用 Excel。
- 读取 XLSX 时显式声明是否有表头；第一行就是数据时使用 `pandas.read_excel(..., header=None)` 或 `read_excel_rows(..., header=False)`，并核对首行、末行与预期行数。
- 模板结构和公式不随意修改，另存到 `PROJECT_ROOT/results/`。
- 公式工作簿使用 `../../../../tools/xlsx/scripts/recalc.py` 重算；失败或超时时原文件不应被覆盖。

## 八、复现清单

示例：

```powershell
python ../scripts/repro_manifest.py `
  --project-root "<PROJECT_ROOT>" `
  --input "<PROJECT_ROOT>/data/input.csv" `
  --seed 42 `
  --parameters '{"alpha":0.1,"max_iter":1000}' `
  --command "python 问题1_求解.py --seed 42" `
  --package numpy --package scipy
```

唯一复现命令必须从 `PROJECT_ROOT` 可直接执行，并生成与论文引用一致的表格和图。

## 九、P2 编程终检

代码、结果表、每类至少 3 张且覆盖全部子问题的三类图和复现清单完成作者自检并冻结后，按 `../../../../references/Subagent调度.md` 派发独立质检 Subagent。质检者重跑唯一复现命令，核对哈希、环境、种子、参数、关键数值、约束、边界、量纲、统计计算和各子问题图表语义；带全部 `--questions` 的 `figure_audit.py --strict` 结果和实际 PNG/灰度预览作为证据输入。`P2` 未返回 `PASS` 不得进入论文阶段。
