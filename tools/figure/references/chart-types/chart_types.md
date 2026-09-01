# 图类型——Nature 图表制作

基础柱状图和趋势图之外的专用图表模式。
每个小节包含从生产脚本中提取的核心代码模式。

---

## 雷达/极坐标图

用于同时跨多个基准对比多个方法。

```python
import numpy as np
import matplotlib.pyplot as plt

def plot_radar(methods, colors, subtask_names, value_matrix,
               benchmark_radii, display_range=(45, 90)):
    """
    参数
    ----------
    methods        : list[str]    — 每条曲线对应一个方法
    colors         : list[str]
    subtask_names  : list[str]    — 每个辐条对应一个子任务（可包含 '\\n'）
    value_matrix   : np.ndarray  — 形状 (n_subtasks, n_methods)
    benchmark_radii: dict         — {基准名: [刻度1, 刻度2, ...]} 用于归一化
    display_range  : (r_min, r_max) — 极坐标径向显示窗口
    """
    r_lo, r_hi = display_range
    n_subtasks = len(subtask_names)
    n_methods  = len(methods)

    fig = plt.figure(figsize=(12, 10))
    ax  = fig.add_subplot(111, projection='polar')

    # 等间距角度，从顶部顺时针
    angles = np.linspace(2 * np.pi, 0, n_subtasks, endpoint=False)
    angles_closed = np.append(angles, angles[0])

    def _normalize(val, bench):
        radii_list = benchmark_radii.get(bench, [0, 100])
        span = max(radii_list) - min(radii_list)
        if span <= 0:
            return (r_lo + r_hi) / 2
        frac = np.clip((val - min(radii_list)) / span, 0, 1)
        return r_lo + (r_hi - r_lo) * frac

    subtask_benchmarks = [s.split('\\n', 1)[-1] if '\\n' in s else s
                          for s in subtask_names]

    # 绘制数据多边形
    for m in range(n_methods):
        norm_vals = np.array([_normalize(value_matrix[i, m], subtask_benchmarks[i])
                              for i in range(n_subtasks)])
        closed = np.append(norm_vals, norm_vals[0])
        ax.plot(angles_closed, closed, color=colors[m], lw=2, label=methods[m])
        ax.fill(angles_closed, closed, color=colors[m], alpha=0.05)
        ax.scatter(angles, norm_vals, color=colors[m], s=18, zorder=5)

    # 样式
    ax.set_ylim(r_lo, r_hi)
    ax.set_theta_zero_location('N')
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(False)

    # 外边界环
    ax.plot(angles_closed, np.full_like(angles_closed, r_hi),
            color='k', lw=0.8, zorder=4)

    # 辐条线
    for a in angles:
        ax.plot([a, a], [r_lo, r_hi], color='gray', lw=0.5, zorder=4)

    # 基准级轮廓多边形
    max_levels = max(len(v) for v in benchmark_radii.values())
    for k in range(max_levels):
        disp = np.array([_normalize(benchmark_radii.get(b, [0,100])[
                            min(k, len(benchmark_radii.get(b,[0,100]))-1)], b)
                         for b in subtask_benchmarks])
        ax.plot(angles_closed, np.append(disp, disp[0]),
                color='k', lw=0.6, zorder=4)

    ax.set_yticks([r_hi])
    ax.set_yticklabels([])
    ax.set_xticks(angles)
    ax.set_xticklabels([])

    # 辐条标签（在外边界环外）
    for angle, label in zip(angles, subtask_names):
        r_label = r_hi + 8 + 10 * abs(np.sin(angle))
        ax.text(angle, r_label, label, fontsize=14,
                ha='center', va='center',
                transform=ax.transData, clip_on=False)

    ax.legend(loc='upper right', bbox_to_anchor=(1.40, 0.05),
              fontsize=15, frameon=False)
    return fig, ax
```

**关键设置**：
- `ax.set_theta_zero_location('N')` — 顶部起始约定
- 移除所有默认边框/网格；手动绘制自定义辐条+轮廓多边形
- 按基准刻度列表将每个辐条独立归一化
- 图例放在**外部** `bbox_to_anchor=(1.40, 0.05)`

---

## 散点图（颜色编码聚类）

```python
def make_scatter(ax, x, y, labels_or_colors,
                 size=50, alpha=0.7, edgecolors='none'):
    """单聚类或多聚类散点。"""
    import numpy as np
    ax.scatter(x, y, c=labels_or_colors, s=size,
               alpha=alpha, edgecolors=edgecolors)
    ax.set_axis_off()   # 概念图用；数据图请移除此行
```

---

## 消融折线面板+参考基线

用于消融比较数据比例、超参数或耦合指标时。

**模式**：
- 用虚线水平基线表示简单/参考模型。
- 用点线水平线表示有意义的操作点，如"25% 数据时的 ours"，仅在文中明确对比时使用。
- 谨慎使用 `twinx()`。如需两个 y 轴，将每个 y 轴标签颜色匹配对应系列，保持刻度范围窄。
- 将图例放在每个面板的低密度区域；如果各面板系列不同，避免一个巨大图例。

```python
fig, axes = plt.subplots(1, 3, figsize=(27, 6),
                         gridspec_kw={"width_ratios": [1.1, 1, 1]})
axes[0].plot(x, baseline, color="black", alpha=0.3, lw=4, ls="--")
axes[0].plot(x, reference, color=hero_color, lw=3, ls=":")
ax2 = axes[2].twinx()
```

---

## 填充面积图（堆叠趋势）

用于累计发表数、堆叠贡献等。

```python
# 填充面积（堆叠）+ 哈希保证打印安全
ax.fill_between(x, 0, y_bottom,
                color='#ffa8a6', label='类别 A')
ax.fill_between(x, 0, y_top,
                color='#9BC8FA',
                hatch='///',               # 黑白打印用哈希
                edgecolor='black',
                label='类别 B')
# 消除边框伪影
ax.fill_between(x, 0, y_top,
                facecolor='none',
                edgecolor='white',
                linewidth=2)

# 叠加趋势线显示精确值
ax.plot(x, y_top, lw=3, color='#13457E')
ax.plot(x, y_bottom, lw=3, color='#850c0a')
```

---

## 对数刻度柱状图

```python
ax.set_yscale('log')
ymin, ymax = ax.get_ylim()
ax.set_ylim(ymin, ymax * 20)   # 扩大顶部空间用于注释

# 在柱上方注释数值
for i, val in enumerate(values):
    ax.text(i, val * 1.1, f'{val:.3f}',
            ha='center', va='bottom', fontsize=16)
```

---

## GridSpec 多面板布局

```python
from matplotlib import gridspec

# 2 行 4 列布局
fig = plt.figure(figsize=(36, 12))
gs = gridspec.GridSpec(2, 4)

ax_top_left  = fig.add_subplot(gs[0, 0])
ax_top_right = fig.add_subplot(gs[0, 1:3])   # 跨第 1-2 列
ax_legend    = fig.add_subplot(gs[0, 3])     # 图例面板
ax_bottom    = fig.add_subplot(gs[1, :])     # 全宽底部
```

---

## Y 轴科学记数法

```python
ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
```

---

## 自定义边框位置

```python
# 将底边框移到 y=0（用于负值）
ax.spines['bottom'].set_position(('data', 0))
ax.xaxis.set_ticks_position('bottom')
ax.spines['left'].set_bounds(0, y_max)
```

---

## 相关文件

- [SKILL.md](../SKILL.md) — 使用场景
- [api.md](api.md) — PALETTE 和核心辅助函数签名
- [common_patterns.md](common_patterns.md) — 柱状图、趋势图和布局模式
- [design_theory.md](design_theory.md) — 原理和配色理论
- [tutorials.md](tutorials.md) — 完整端到端演练
