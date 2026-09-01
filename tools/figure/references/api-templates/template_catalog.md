# 验证过的绘图模板目录

在后端已选定 Python 后使用本目录。这些模板使用 NumPy 和 Matplotlib，
需要真实 CSV 输入用于生产，输出 SVG、PDF 和 QA 记录。

## 模板列表

| 模板 | CSV 必需列 | 主要保护措施 |
|---|---|---|
| `roc` | 一个 FPR 列 + 一个或多个 TPR 列 | `[0,1]` 范围检查、稳定 FPR 排序、梯形 AUC 记录 |
| `heatmap` | 行标签、列标签、值矩阵 | 完整类别验证、无静默类别移除 |
| `convergence` | 迭代次数 + 一个或多个目标值列 | 单调性检查（可选）、NaN 处理 |
| `scatter_xy` | x, y, 可选 group | 过绘检查、自动推荐 hexbin |

## ROC 曲线模板

```python
def plot_roc(ax, fpr, tpr, label='', color='#0072B2'):
    """绘制 ROC 曲线并计算 AUC。"""
    import numpy as np
    # 范围检查
    assert np.all(fpr >= 0) and np.all(fpr <= 1), "FPR 必须在 [0,1]"
    assert np.all(tpr >= 0) and np.all(tpr <= 1), "TPR 必须在 [0,1]"
    # 按 FPR 排序
    order = np.argsort(fpr)
    fpr_sorted = fpr[order]
    tpr_sorted = tpr[order]
    # 梯形 AUC
    auc = np.trapz(tpr_sorted, fpr_sorted)
    ax.plot(fpr_sorted, tpr_sorted, color=color, lw=1.2,
            label=f'{label} (AUC = {auc:.3f})')
    ax.plot([0, 1], [0, 1], '--', color='#6B7280', lw=0.8, alpha=0.5)
    ax.set(xlabel='假阳性率', ylabel='真阳性率', xlim=(0, 1), ylim=(0, 1))
    ax.legend(fontsize=6.5, frameon=False)
    return auc
```

**CSV 格式**：

```csv
fpr,model_a,model_b
0.0,0.0,0.0
0.01,0.15,0.08
0.05,0.45,0.32
...
1.0,1.0,1.0
```

## 热力图模板

```python
def plot_validated_heatmap(ax, matrix, x_labels=None, y_labels=None,
                           cmap='RdBu_r', annotate=True, fmt='{:.2f}'):
    """带验证的热力图。"""
    import numpy as np
    import matplotlib as mpl
    matrix = np.asarray(matrix)
    assert matrix.ndim == 2, "矩阵必须是 2D"
    if x_labels:
        assert len(x_labels) == matrix.shape[1], "x_labels 长度必须等于列数"
    if y_labels:
        assert len(y_labels) == matrix.shape[0], "y_labels 长度必须等于行数"

    im = ax.imshow(matrix, cmap=cmap, aspect='auto')
    cbar = ax.figure.colorbar(im, ax=ax, shrink=0.8)
    if annotate:
        norm = mpl.colors.Normalize(vmin=matrix.min(), vmax=matrix.max())
        cm_obj = plt.get_cmap(cmap)
        for (i, j), val in np.ndenumerate(matrix):
            r, g, b, _ = cm_obj(norm(val))
            lum = 0.299*r + 0.587*g + 0.114*b
            color = 'white' if lum < 0.5 else '#333333'
            ax.text(j, i, fmt.format(val), ha='center', va='center',
                    fontsize=6, color=color)
    if x_labels:
        ax.set_xticks(range(len(x_labels)))
        ax.set_xticklabels(x_labels, rotation=30, ha='right', fontsize=6)
    if y_labels:
        ax.set_yticks(range(len(y_labels)))
        ax.set_yticklabels(y_labels, fontsize=6)
    ax.set_frame_on(False)
```

## 收敛曲线模板

```python
def plot_convergence(ax, iterations, values, label='', color='#0072B2',
                     show_std=False, std_vals=None):
    """绘制收敛曲线，可选置信区间。"""
    import numpy as np
    ax.plot(iterations, values, color=color, lw=1.2, label=label)
    if show_std and std_vals is not None:
        ax.fill_between(iterations, values - std_vals, values + std_vals,
                        color=color, alpha=0.12)
    ax.set_xlabel('迭代次数', fontsize=7)
    ax.set_ylabel('目标函数值', fontsize=7)
    ax.tick_params(labelsize=6)
    ax.legend(fontsize=6.5, frameon=False)
```

## 约定

- 模板不计算假设检验。统计只在定义重复单元、检验、假设、
  多重校正和图注报告契约后添加。
- 永远不要用 `--demo` 作为稿件交付物。
- 如果缺少必要的数值数据或非有限值，默认行为是停止。
