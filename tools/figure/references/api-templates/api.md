# API 参考 — 可复用绘图辅助函数

约定、常量和可复用代码块。在脚本中实现或按需适配。

---

## 强制规则（每个脚本顶部）

以下三行**不可协商**，必须出现在每个脚本顶部、创建任何图形之前：

```python
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
plt.rcParams['svg.fonttype'] = 'none'   # 保持文字为 <text> 节点而非路径
```

**为什么 `svg.fonttype = 'none'`**：matplotlib 默认 `'path'` 把每个字形转为贝塞尔路径，
导致文字不可选、不可搜索、无法在 Illustrator/Inkscape 中重新对齐。设为 `'none'` 后，
文字保持 SVG `<text>` 元素，字体替换在渲染时发生。

---

## 辅助函数

### is_dark(hex_color, threshold=128)

```python
def is_dark(hex_color, threshold=128):
    """判断十六进制颜色是否偏暗（用于选择白色/黑色文字）。"""
    c = hex_color.lstrip('#')
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    return (0.299*r + 0.587*g + 0.114*b) < threshold
```

### add_panel_label(ax, label, ...)

```python
def add_panel_label(ax, label, x=-0.06, y=1.02, fontsize=14,
                    color='black', fontweight='bold'):
    """放置 Nature 风格的面板标签（左上角小写粗体）。"""
    ax.text(x, y, label, transform=ax.transAxes,
            fontsize=fontsize, fontweight=fontweight, color=color,
            ha='left', va='bottom')
```

### make_grouped_bar(ax, categories, series, labels, ...)

```python
def make_grouped_bar(ax, categories, series, labels,
                     ylabel='Value', colors=None,
                     annotate=False, bar_width=0.8, error_kw=None):
    """
    分组柱状图：多方法在多指标上的对比。

    参数
    ----------
    ax         : matplotlib Axes
    categories : list[str]  — x 轴类别名（长度 K）
    series     : list[array] — 每组一个数组（每个长度 K）
    labels     : list[str]  — 每组的图例标签
    ylabel     : str
    colors     : list[str] | None — 默认使用 COLOR_SEQUENCE
    annotate   : bool  — 在每根柱上方打印数值
    bar_width  : float — 每个类别的总宽度
    error_kw   : dict  — 传给 ax.bar 的 error_kw

    返回
    -------
    list[BarContainer]
    """
    import numpy as np
    if colors is None:
        from .style_constants import COLOR_SEQUENCE
        colors = list(COLOR_SEQUENCE)
    if error_kw is None:
        error_kw = {'elinewidth': 1.5, 'capthick': 1.5, 'capsize': 4}
    n_groups = len(series)
    n_cats = len(categories)
    w = bar_width / n_groups
    x = np.arange(n_cats)
    containers = []
    for i, (vals, label, color) in enumerate(zip(series, labels, colors)):
        offset = (i - (n_groups - 1) / 2) * w
        bars = ax.bar(x + offset, vals, width=w, label=label,
                      color=color, edgecolor='white', linewidth=0.5,
                      error_kw=error_kw)
        containers.append(bars)
        if annotate:
            for bar, val in zip(bars, vals):
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 0.01,
                        f'{val:.2f}', ha='center', va='bottom', fontsize=6)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=6.5)
    ax.set_ylabel(ylabel, fontsize=8)
    ax.legend(fontsize=6.5, frameon=False)
    return containers
```

### make_trend(ax, x, y_series, labels, ...)

```python
def make_trend(ax, x, y_series, labels,
               colors=None, ylabel=None, xlabel=None,
               show_shadow=False, shadow_alpha=0.15,
               lw=1.5, marker='o', markersize=4):
    """
    多线趋势图。

    参数
    ----------
    x        : array-like   — 共享 x 值
    y_series : list[array]  — 每条线一个 1D 数组
    labels   : list[str]
    show_shadow : bool  — 若 y_series 包含 2D 数组（行=多次运行），填充 ± std
    """
    import numpy as np
    if colors is None:
        from .style_constants import COLOR_SEQUENCE
        colors = list(COLOR_SEQUENCE)
    for y, label, color in zip(y_series, labels, colors):
        y = np.asarray(y)
        if y.ndim == 2:
            mean, std = y.mean(0), y.std(0)
        else:
            mean, std = y, None
        ax.plot(x, mean, color=color, lw=lw, marker=marker,
                markersize=markersize, label=label)
        if show_shadow and std is not None:
            ax.fill_between(x, mean - std, mean + std,
                            color=color, alpha=shadow_alpha)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=8)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=8)
    ax.legend(fontsize=6.5, frameon=False)
```

### make_forest_plot(ax, labels, estimates, ci_low, ci_high, ...)

```python
def make_forest_plot(ax, labels, estimates, ci_low, ci_high,
                     colors=None, ref=0.0, xlabel=None, xlim=None,
                     marker='o', markersize=4, lw=1.2):
    """
    森林图：用于多指标综合评价、灵敏度分析。
    """
    import numpy as np
    y = np.arange(len(labels))[::-1]
    if colors is None:
        colors = ['#D55E00'] * len(labels)
    for yi, est, lo, hi, color in zip(y, estimates, ci_low, ci_high, colors):
        ax.plot([lo, hi], [yi, yi], color=color, lw=lw)
        ax.plot(est, yi, marker=marker, ms=markersize, color=color)
    ax.axvline(ref, color='#6B7280', linestyle='--', linewidth=0.8, alpha=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=8)
    if xlim is not None:
        ax.set_xlim(xlim)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
```

### make_heatmap(ax, matrix, ...)

```python
def make_heatmap(ax, matrix, x_labels=None, y_labels=None,
                 cmap='RdBu_r', cbar_label=None, annotate=False,
                 fmt='{:.2f}', fontsize=6):
    """
    2D 热力图：相关性矩阵、混淆矩阵、灵敏度热图。
    """
    import numpy as np
    import matplotlib as mpl
    im = ax.imshow(matrix, cmap=cmap, aspect='auto')
    if cbar_label:
        cbar = ax.figure.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label(cbar_label, fontsize=7)
    if x_labels:
        ax.set_xticks(range(len(x_labels)))
        ax.set_xticklabels(x_labels, rotation=30, ha='right', fontsize=6)
    if y_labels:
        ax.set_yticks(range(len(y_labels)))
        ax.set_yticklabels(y_labels, fontsize=6)
    if annotate:
        norm = mpl.colors.Normalize(vmin=matrix.min(), vmax=matrix.max())
        cm_obj = plt.get_cmap(cmap)
        for (i, j), val in np.ndenumerate(matrix):
            r, g, b, _ = cm_obj(norm(val))
            lum = 0.299*r + 0.587*g + 0.114*b
            color = 'white' if lum < 0.5 else '#333333'
            ax.text(j, i, fmt.format(val), ha='center', va='center',
                    fontsize=fontsize, color=color)
    ax.set_frame_on(False)
```

### finalize_figure(fig, out_path, ...)

```python
def finalize_figure(fig, out_path, formats=None, dpi=300,
                    pad=1, close=True):
    """
    应用 tight_layout 并保存图形。

    参数
    ----------
    out_path : str   — 无扩展名路径，或带扩展名
    formats  : list  — 如 ['png', 'pdf']。None 则用 out_path 的扩展名。
    dpi      : int   — 300 标准，600 用于密集柱状图
    """
    import os
    from pathlib import Path
    fig.tight_layout(pad=pad)
    base = Path(out_path)
    os.makedirs(base.parent, exist_ok=True)
    if formats is None:
        formats = [base.suffix.lstrip('.') or 'png']
        base = base.with_suffix('')
    saved = []
    for fmt in formats:
        p = str(base) + f'.{fmt}'
        fig.savefig(p, dpi=dpi)
        saved.append(p)
    if close:
        plt.close(fig)
    return saved
```

---

## 验证规则

- `make_grouped_bar`：`len(categories)` 必须等于 `series` 中每个数组的长度。
- `make_trend`：`y_series` 中每个数组长度必须与 `x` 相同。
- `make_heatmap`：`matrix` 必须是 2D；`x_labels` 长度 = `matrix.shape[1]`；
  `y_labels` 长度 = `matrix.shape[0]`。
- `finalize_figure`：支持格式 — `png`、`pdf`、`svg`、`eps`、`jpg`、`tif`。

---

## 约定

- 输出保存在 `PROJECT_ROOT/figures/` 下；`finalize_figure` 自动创建父目录。
- 在无头/批量运行中，导入 pyplot 前设置非交互后端：
  ```python
  import matplotlib
  matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  ```
- 保存后始终 `plt.close(fig)` 释放内存。
- 多面板图中，优先一个基线色系加一个主色系；保留绿/红用于增减方向提示。
- 当颜色角色、分辨率或布局未指定且会改变图形时，最终化前与用户确认。
