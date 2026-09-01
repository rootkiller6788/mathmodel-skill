# 常用布局模式——Nature 图表制作

出版级脚本中可复用的布局和编码模式。

---

## 模式 1：超宽多指标柱状面板

3–4 个指标跨多个方法对比时，使用宽画布避免柱和标签拥挤。

```python
fig = plt.figure(figsize=(45, 12))   # 或 (28, 6) 用于较少指标
gs = gridspec.GridSpec(1, n_metrics)

for i, metric in enumerate(metrics):
    ax = fig.add_subplot(gs[i])
    ax.bar(x, values[metric], color=colors, ...)
    ax.set_ylabel(metric, fontsize=54, labelpad=12)
    ax.set_xticks([])

# 最后一个面板：仅图例
ax_leg = fig.add_subplot(gs[-1])
ax_leg.legend(handles, labels, fontsize=38, loc='center', frameon=False)
ax_leg.set_axis_off()

fig.tight_layout(pad=2)
```

**规则**：宽度通常 3–4× 高度。便于从左到右阅读。

---

## 模式 2：专用图例面板

图例较大时，给它单独的轴，保持数据面板整洁。

```python
fig, axes = plt.subplots(1, n_data + 1, figsize=(...))

for i, ax in enumerate(axes[:-1]):
    bars = ax.bar(...)
    if i == 0:
        handles, labels = ax.get_legend_handles_labels()

# 仅图例面板
axes[-1].legend(handles, labels, fontsize=28, loc='center', frameon=False)
axes[-1].set_axis_off()
```

---

## 模式 3：分类柱状图隐藏 x 轴刻度

方法在图例中命名时，完全隐藏 x 轴刻度。

```python
ax.set_xticks([])        # 移除刻度和标签
# 或：
ax.set_xticklabels([])   # 保留刻度线，移除标签
```

---

## 模式 4：动态 y 轴收紧

值在 80–95 范围时，永远不要用 0–100。

```python
margin = (values.max() - values.min()) * 0.1   # 10% 留白
ax.set_ylim([values.min() - margin, values.max() + margin])

# 在整数刻度位置手动设置刻度
ax.set_yticks([0.75, 0.80, 0.85, 0.90])
ax.tick_params(axis='y', labelsize=36, length=10, width=2)
```

---

## 模式 5：Alpha 渐变消融柱（同一颜色，不同透明度）

```python
import numpy as np

blue_rgb = (0.215686, 0.458824, 0.729412)   # #3775BA 浮点元组
n_ablations = len(ablation_configs)
alphas = np.linspace(0.2, 1.0, n_ablations)
colors = [(blue_rgb[0], blue_rgb[1], blue_rgb[2], a) for a in alphas]
# 完整方法 → alpha=1.0，最大消融 → alpha=0.2
```

---

## 模式 6：哈希编码（黑白打印安全）

添加哈希使柱在黑白打印时仍可区分。

```python
hatches = ['/', '\\\\', '.', 'x', 'o', '+']
for bar_container, hatch in zip(grouped_bars, hatches):
    for patch in bar_container:
        patch.set_hatch(hatch)
        patch.set_edgecolor('black')
        patch.set_linewidth(1.5)
```

---

## 模式 7：语义或族系颜色映射

所有面板中始终保持颜色一致映射：

```python
method_colors = {
    'ResNet1d18': '#484878',   # baseline_dark
    'ResNet1d34': '#7884B4',   # baseline_mid
    'ECGFounder': '#B4C0E4',   # baseline_soft
    'CSFM-Tiny':  '#E4E4F0',   # ours_tiny
    'CSFM-Base':  '#E4CCD8',   # ours_base
    'CSFM-Large': '#F0C0CC',   # ours_large
}
colors = [method_colors[m] for m in methods]
```

优先使用连贯的色相族系，而非因类别不同就交替使用饱和蓝/绿/红。绿色和红色通常应保留给 **方向标注**，而非主系列标识：

```python
ax.scatter(x_gain, y_gain, marker='^', color='#2E9E44', s=90, zorder=6)  # 改进
ax.scatter(x_drop, y_drop, marker='v', color='#E53935', s=90, zorder=6)  # 退化
```

---

## 模式 8：柱内文字（亮度感知颜色）

```python
def annotate_bars(ax, bars, colors, fmt='{:.2f}', fontsize=32, offset=-0.10):
    for bar, color in zip(bars, colors):
        c = color.lstrip('#')
        r, g, b = int(c[0:2],16)/255, int(c[2:4],16)/255, int(c[4:6],16)/255
        lum = 0.299*r + 0.587*g + 0.114*b
        textcolor = 'white' if lum < 0.5 else 'black'
        value = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2,
                value + offset,
                fmt.format(value),
                ha='center', va='bottom',
                fontsize=fontsize, color=textcolor)
```

---

## 模式 9：填充趋势+哈希（打印安全）

```python
ax.fill_between(x, 0, cumsum_series,
                color=fill_color,
                hatch='\\\\\\',   # 三反斜线密集哈希
                edgecolor='black',
                label=label_name)
# 视觉消除边框伪影：
ax.fill_between(x, 0, cumsum_series,
                facecolor='none',
                edgecolor='white',
                linewidth=2)
```

---

## 模式 10：在趋势线上标注事件

```python
def mark_events(ax, x_labels, y_cumsum, events_dict, dy_fraction=0.1):
    """在趋势线的事件日期处添加带标签的箭头。"""
    x_index = {label: i for i, label in enumerate(x_labels)}
    y_lo, y_hi = ax.get_ylim()
    dy = dy_fraction * (y_hi - y_lo)
    for date, label in events_dict.items():
        if date not in x_index:
            continue
        i = x_index[date]
        stars = label.count('*')
        clean_label = label.replace('*', '')
        y_data = y_cumsum[i]
        ax.annotate(
            clean_label,
            xy=(i, y_data),
            xytext=(i, y_data + (1 + 0.8 * stars) * dy),
            ha='center', va='bottom', fontsize=11,
            arrowprops=dict(arrowstyle='-|>', lw=1.3, color='black',
                            shrinkA=0, shrinkB=0, mutation_scale=15)
        )
```

---

## 模式 11：分组柱状图（组内分组）

```python
num_methods = len(methods)
xtick_positions = []

for dataset_idx, dataset_name in enumerate(datasets):
    x_start = dataset_idx * (num_methods + 1)   # 组间间隔为 1
    ax.bar(
        np.arange(num_methods) + x_start,
        values[dataset_name],
        color=method_colors,
        label=methods if dataset_idx == 0 else ['_nolegend_'] * num_methods,
    )
    xtick_positions.append(np.mean(np.arange(num_methods)) + x_start)

ax.set_xticks(xtick_positions)
ax.set_xticklabels(datasets)
```

---

## 模式 12：示意图英雄面板+支撑量化行

用于一个机制或制造故事需要主导，下方放 2–4 个较小的证据图。

```python
fig = plt.figure(figsize=(7.2, 6.2))
gs = fig.add_gridspec(
    2, 4,
    height_ratios=[2.2, 1.0],
    hspace=0.18, wspace=0.28,
)

ax_top = fig.add_subplot(gs[0, :])    # 英雄示意图
ax_b = fig.add_subplot(gs[1, 0])
ax_c = fig.add_subplot(gs[1, 1:3])
ax_d = fig.add_subplot(gs[1, 3])

# 顶部面板承载主配色和主视觉叙事
```

规则：

- 分配总高度的 45–60% 给英雄示意图。
- 下方图表复用同一颜色的柔和版本。
- 支撑图比英雄面板更安静。

---

## 模式 13：非对称英雄面板

用于一个面板在概念上居于核心地位并应主导时。

```python
fig = plt.figure(figsize=(7.2, 5.8))
gs = fig.add_gridspec(3, 4, hspace=0.25, wspace=0.28)

ax_a = fig.add_subplot(gs[0, :2])
ax_b = fig.add_subplot(gs[0, 2])
ax_c = fig.add_subplot(gs[1, :2])
ax_d = fig.add_subplot(gs[1, 2])
ax_e = fig.add_subplot(gs[:, 3])      # 英雄面板跨所有行
ax_f = fig.add_subplot(gs[2, :2])
```

规则：如果科学重要性不等，不要将所有子图归一化为相同大小。

---

## 模式 14：直接标注填充区域

用于相同分类结构重复且图例过大时。

```python
for x_text, y_text, text, color in label_specs:
    ax.text(
        x_text, y_text, text,
        color=color,
        ha='center', va='center',
        fontsize=9, fontweight='bold',
    )
```

规则：

- 标签保持在稳定、视觉上较大的区域。
- 填充变化强烈时使用小号白色或黑色描边。
- 对重复的堆叠面积图或相位图，优先使用直接标注而非超大图例。

---

## 相关文件

- [SKILL.md](../SKILL.md) — 使用场景
- [api.md](api.md) — 辅助函数签名和 PALETTE
- [design_theory.md](design_theory.md) — 每个模式背后的原理
- [nature_2026_observations.md](nature_2026_observations.md) — 这些模式背后的真实 Nature 页面原型
- [tutorials.md](tutorials.md) — 端到端演练
- [chart_types.md](chart_types.md) — 雷达图、3D 图、散点图模式
