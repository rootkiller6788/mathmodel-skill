# 教程 — 数学建模可视化

最常见的出版级图形类型的端到端演练。所有示例使用 `api.md` 中的辅助函数和
`common_patterns.md` 中的布局模式。

---

## 教程 1：分组柱状图（多方法多指标对比）

**目标**：多种方法在多个指标上对比，图例放在专用面板中。

```python
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec

# --- 样式 ---
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['font.size'] = 8
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.linewidth'] = 0.7

# --- 数据 ---
methods = ['PSO', 'GA', 'SA', 'DE', 'ABC', 'GWO']
colors  = ['#0072B2', '#E69F00', '#009E73', '#D55E00', '#CC79A7', '#56B4E9']
metrics = ['收敛精度', '收敛速度', '稳定性']
mean = {
    '收敛精度': np.array([0.85, 0.82, 0.78, 0.88, 0.86, 0.84]),
    '收敛速度': np.array([0.72, 0.68, 0.81, 0.75, 0.70, 0.77]),
    '稳定性': np.array([0.65, 0.71, 0.69, 0.73, 0.67, 0.70]),
}
std = {k: v * 0.03 for k, v in mean.items()}

# --- 图形 ---
fig = plt.figure(figsize=(7.2, 2.8))
gs = gridspec.GridSpec(1, len(metrics) + 1, width_ratios=[1]*len(metrics) + [0.6])

handles, labels = None, None
for col, metric in enumerate(metrics):
    ax = fig.add_subplot(gs[col])
    bars = ax.bar(
        range(len(methods)), mean[metric], yerr=std[metric],
        capsize=3, color=colors, label=methods,
        error_kw={'elinewidth': 1, 'capthick': 1},
    )
    if col == 0:
        handles, labels = ax.get_legend_handles_labels()
    ax.set_xticks([])
    y_vals = mean[metric]
    margin = (y_vals.max() - y_vals.min()) * 0.15
    ax.set_ylim([y_vals.min() - margin, y_vals.max() + margin])
    ax.set_ylabel(metric, fontsize=8)

# 图例专用面板
ax_leg = fig.add_subplot(gs[-1])
ax_leg.legend(handles, labels, fontsize=6.5, loc='center', frameon=False)
ax_leg.set_axis_off()

fig.tight_layout(pad=1)
os.makedirs('./figures', exist_ok=True)
fig.savefig('./figures/comparison.png', dpi=300)
fig.savefig('./figures/comparison.pdf')
plt.close(fig)
```

---

## 教程 2：收敛曲线（趋势 + 置信区间）

**目标**：多算法收敛过程对比，展示均值 ± 标准差。

```python
import os
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['font.size'] = 8
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.linewidth'] = 0.7

methods = ['PSO', 'GA', 'DE', 'GWO']
colors  = ['#0072B2', '#E69F00', '#D55E00', '#56B4E9']
x = np.arange(0, 200, 1)

fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0))

for ax, (panel_name, base_loss) in zip(axes, [('F1 测试函数', 500), ('F2 测试函数', 300)]):
    for method, color in zip(methods, colors):
        y_mean = base_loss * np.exp(-x / 40) + np.random.randn(len(x)) * 2
        y_std = np.abs(np.random.randn(len(x)) * 5 + 3)
        ax.plot(x, y_mean, color=color, lw=1.2, label=method)
        ax.fill_between(x, y_mean - y_std, y_mean + y_std, color=color, alpha=0.12)
    ax.set_title(panel_name, fontsize=8)
    ax.set_xlabel('迭代次数', fontsize=7)
    ax.set_ylabel('目标函数值', fontsize=7)
    ax.tick_params(labelsize=6)
    if panel_name == 'F1 测试函数':
        handles, labels = ax.get_legend_handles_labels()

# 图例放在最后一个 axes
axes[-1].legend(handles, labels, fontsize=6.5, frameon=False)

fig.tight_layout(pad=1)
os.makedirs('./figures', exist_ok=True)
fig.savefig('./figures/convergence.png', dpi=300)
fig.savefig('./figures/convergence.pdf')
plt.close(fig)
```

---

## 教程 3：热力图（灵敏度分析 / 相关性矩阵）

**目标**：参数灵敏度热力图，单元格自动对比文字。

```python
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['font.size'] = 8
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.linewidth'] = 0.7

# 灵敏度矩阵：行=参数，列=指标
params = ['种群规模', '迭代次数', '交叉率', '变异率', '温度衰减']
metrics = ['精度', '速度', '稳定性', '鲁棒性']
matrix = np.array([
    [0.85, 0.42, 0.68, 0.71],
    [0.72, 0.88, 0.55, 0.63],
    [0.31, 0.25, 0.78, 0.45],
    [0.48, 0.19, 0.82, 0.52],
    [0.22, 0.65, 0.38, 0.76],
])

fig, ax = plt.subplots(figsize=(5.5, 3.5))
im = ax.imshow(matrix, cmap='RdBu_r', aspect='auto', vmin=0, vmax=1)

# 添加 colorbar
cbar = fig.colorbar(im, ax=ax, shrink=0.8)
cbar.set_label('灵敏度系数', fontsize=7)
cbar.ax.tick_params(labelsize=6)

# 标注数值
norm = mpl.colors.Normalize(vmin=0, vmax=1)
cm = plt.get_cmap('RdBu_r')
for (i, j), val in np.ndenumerate(matrix):
    r, g, b, _ = cm(norm(val))
    lum = 0.299*r + 0.587*g + 0.114*b
    color = 'white' if lum < 0.5 else '#333333'
    ax.text(j, i, f'{val:.2f}', ha='center', va='center', fontsize=6, color=color)

ax.set_xticks(range(len(metrics)))
ax.set_xticklabels(metrics, fontsize=7)
ax.set_yticks(range(len(params)))
ax.set_yticklabels(params, fontsize=7)

fig.tight_layout(pad=1)
os.makedirs('./figures', exist_ok=True)
fig.savefig('./figures/sensitivity.png', dpi=300)
fig.savefig('./figures/sensitivity.pdf')
plt.close(fig)
```

---

## 教程 4：森林图（多指标综合评价）

**目标**：多个方案在综合得分上的点估计 + 置信区间。

```python
import os
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['font.size'] = 8
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.linewidth'] = 0.7

labels = ['方案 A', '方案 B', '方案 C', '方案 D', '方案 E', '基准']
estimates = np.array([0.88, 0.82, 0.79, 0.85, 0.76, 0.70])
ci_low  = estimates - np.array([0.03, 0.04, 0.05, 0.03, 0.04, 0.0])
ci_high = estimates + np.array([0.02, 0.03, 0.04, 0.02, 0.03, 0.0])

fig, ax = plt.subplots(figsize=(5, 3))
y = np.arange(len(labels))[::-1]

for yi, est, lo, hi in zip(y, estimates, ci_low, ci_high):
    color = '#0072B2' if est > 0.8 else '#E69F00'
    ax.plot([lo, hi], [yi, yi], color=color, lw=1.2)
    ax.plot(est, yi, marker='o', ms=4, color=color)

ax.axvline(0.70, color='#6B7280', linestyle='--', linewidth=0.8, alpha=0.8, label='基准线')
ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=7)
ax.set_xlabel('综合得分', fontsize=8)
ax.legend(fontsize=6.5, frameon=False)

fig.tight_layout(pad=1)
os.makedirs('./figures', exist_ok=True)
fig.savefig('./figures/forest.png', dpi=300)
fig.savefig('./figures/forest.pdf')
plt.close(fig)
```

---

## 相关文件

- [SKILL.md](../SKILL.md) — 何时使用本工具
- [api.md](api.md) — 可复用辅助函数实现
- [common_patterns.md](common_patterns.md) — 上述示例使用的布局模式
- [design_theory.md](design_theory.md) — 这些选择背后的原因
- [chart_types.md](chart_types.md) — 雷达图、3D、散点、填充图
