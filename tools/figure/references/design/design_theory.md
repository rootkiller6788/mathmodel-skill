# Nature 图表设计理论

源自 [figures4papers](https://github.com/ChenLiu-1996/figures4papers) 仓库中的脚本（发表于 *Nature Machine Intelligence* 及顶级 ML/生物信息学会议）。

---

## 1) 字体

### 字体栈（优先级）
- **Nature 标准**：`font.family = 'sans-serif'`，`font.sans-serif = ['Arial']`
- **降级栈**：`['Arial', 'Helvetica', 'DejaVu Sans', 'sans-serif']`
- **Helvetica**（等效）在许多脚本中写作 `font.family = 'helvetica'`
- SVG/PDF 可编辑文本：始终设置 `svg.fonttype = 'none'`
- LaTeX 数学标签：仅在安装 LaTeX 时使用 `text.usetex = True`

### 字号层级
| 场景 | font.size | axes.linewidth |
|------|-----------|---------------|
| 期刊终版密集多面板（出版宽度） | 7–9 | 0.8–1.2 |
| 大型对比柱状图（figsize > 28in） | 24 | 3 |
| 紧凑子图 / 分析图 | 15–16 | 2 |
| 大面板轴标签 | 32–54（逐标签覆盖） | — |
| 柱内注释 | 32–36 | — |
| 大面板图例文字 | 28–38 | — |
| 刻度标签 | 20–36 | — |

目标 Nature 双栏终版尺寸时，从比幻灯片预览图更小的字号起步。2026 年采样论文在密集复合图中通常最终使用 7–9pt。

---

## 2) 坐标轴与边框

```python
plt.rcParams['axes.spines.right'] = False   # 始终关闭
plt.rcParams['axes.spines.top'] = False     # 始终关闭
plt.rcParams['legend.frameon'] = False      # 无边框图例
```

- 仅保留左+下边框——极简风格，Nature 推荐。
- 默认无网格线；用稀疏的 y 轴刻度引导视线。

### 线宽规范

| 线条类型 | 推荐宽度 | 说明 |
|----------|---------|------|
| 折线（plot） | 0.8–1.2 pt | Nature 密集复合图标准；低于 0.8 pt 小尺寸下不可读 |
| 坐标轴边框（axes.linewidth） | 0.8–1.2 pt | 与折线匹配 |
| 柱边框（edgecolor） | 0.5–1.0 pt | 白色边框分隔相邻柱；或黑色边框强调轮廓 |
| 误差棒（errorbar） | 0.8–1.0 pt | capsize=3–5 |
| 参考线（axhline/axvline） | 0.6–0.8 pt | 灰色虚线，低于数据线粗细 |
| 网格线（如需要） | 0.3–0.5 pt | 极淡灰色，仅在数据密集时辅助读数 |

```python
# 全局线宽设置
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['lines.linewidth'] = 1.0
plt.rcParams['patch.linewidth'] = 0.5
plt.rcParams['grid.linewidth'] = 0.3
```

---

## 3) 配色方案

语义：蓝色 = 提出方法，绿色 = 正向变体，红/粉 = 基线方法，中性 = 参考/背景。但在密集多面板图中，**族系一致性优先于最大色相分离**。

```python
PALETTE = {
    # 提出/关键方法
    "blue_main":      "#0F4D92",   # 深蓝——核心方法
    "blue_secondary": "#3775BA",   # 中蓝——第二方法

    # 正向/改进色阶（浅→深）
    "green_1": "#DDF3DE",
    "green_2": "#AADCA9",
    "green_3": "#8BCF8B",

    # 基线/对比色阶（浅→深）
    "red_1":      "#F6CFCB",
    "red_2":      "#E9A6A1",
    "red_strong": "#B64342",

    # 中性支撑
    "neutral_light": "#CFCECE",
    "neutral_mid":   "#767676",
    "neutral_dark":  "#4D4D4D",
    "neutral_black": "#272727",

    # 强调（少量使用）
    "gold":   "#FFD700",
    "teal":   "#42949E",
    "violet": "#9A4D8E",
    "magenta":"#EA84DD",
}

DEFAULT_COLOR_ORDER = [
    "#0F4D92",   # blue_main
    "#8BCF8B",   # green_3
    "#B64342",   # red_strong
    "#42949E",   # teal
    "#9A4D8E",   # violet
    "#CFCECE",   # neutral_light
]
```

### 统一族系规则（推荐用于 NMI 风格页面）

出版图应读起来像 **一张图**，而非六个无关图表。基线方法统一用冷色族系，提出方法用紫/玫瑰族系。

```python
PALETTE_NMI_PASTEL = {
    "baseline_dark": "#484878",
    "baseline_mid":  "#7884B4",
    "baseline_soft": "#B4C0E4",
    "ours_tiny":  "#E4E4F0",
    "ours_base":  "#E4CCD8",
    "ours_large": "#F0C0CC",
    "delta_up":   "#2E9E44",
    "delta_down": "#E53935",
}

DEFAULT_COLOR_ORDER_NMI_PASTEL = [
    "#484878",   # baseline_dark
    "#7884B4",   # baseline_mid
    "#B4C0E4",   # baseline_soft
    "#E4E4F0",   # ours_tiny
    "#E4CCD8",   # ours_base
    "#F0C0CC",   # ours_large
]
```

规则：
1. 相关基线统一用冷色族系。
2. 变体（Tiny/Base/Large）统一用核心色族系。
3. 绿色/红色仅用于箭头、增减、阈值或有符号方向标注。
4. 同一方法在不同面板中不要映射到不同色相族系。
5. 拿不准时，降低饱和度优于增加类别。

### 消融实验 Alpha 编码
消融同一方法的组件时，用 **单一颜色+不同透明度**：
```python
color = (0.215686, 0.458824, 0.729412)   # blue_secondary RGB
alphas = np.linspace(0.2, 1.0, n_variants)
colors = [(color[0], color[1], color[2], a) for a in alphas]
# alpha=1.0 → 完整方法，alpha=0.2 → 最小消融变体
```

---

## 4) 布局与构图

### 图尺寸
| 图类型 | 典型 figsize |
|--------|-------------|
| 期刊宽度复合页 / 非对称多面板 | (7.0–7.4, 5.5–7.8) |
| 多指标柱状图（3–4 指标+图例） | (28–45, 6–12) |
| 紧凑单柱状图 | (9–16, 5–8) |
| 趋势/折线多面板 | (14, 4) 或 (9, 8) |
| 热力图单图 | (8–20, 5–9) |
| 雷达极坐标图 | (12, 10) |
| 多面板复合图 | (24, 8) |

**规则**：宽度 ≈ 3–4× 高度（对比柱状图）；避免纵向拥挤，便于从左到右阅读。

### 专用图例面板
多轴图中，**最后一个子图专门放图例**：
```python
ax_legend = fig.add_subplot(1, n+1, n+1)
ax_legend.legend(handles, labels, fontsize=..., loc='center', frameon=False)
ax_legend.set_axis_off()
```

### 动态 y 轴缩放
值集中在窄区间时，永远不要用固定的 0–100。
收紧到数据范围：`ax.set_ylim([data.min() - margin, data.max() + margin])`。

### 面板标签与间距

- 在左上角附近使用小号加粗小写字母面板标签。
- 间距紧凑但真实；深色和浅色模块相邻时增大间距。
- 底部有密集图注时，留出额外底部空间。
- 避免装饰性面板边框。对齐和空白应承载结构。

### 图例精简与直接标注

- 区域、通道或线条身份空间稳定时使用直接标注。
- 优先在行上方使用共享图例条，而非在多个轴内重复图例。
- 密集分类面积图内嵌文字通常比分离图例更清晰。
- 图例应无边框且视觉上弱于数据。

### X 轴刻度隐藏
当柱状图代表方法且图例已命名时：
```python
ax.set_xticks([])   # 隐藏 x 轴标签；用图例+面板标题替代
```

---

## 5) 柱状图规则

### 垂直柱状图（对比）
```python
bars = ax.bar(
    x_positions,
    values,
    yerr=std_values,
    capsize=5,
    color=colors,
    label=method_names,
    edgecolor='black',      # 清晰分隔
    linewidth=1.5,
)
```

### 水平柱状图（消融）
```python
ax.barh(
    y_positions,
    values,
    xerr=std_values,
    color=[(r, g, b, alpha) for alpha in alphas],
    ecolor='k',
    capsize=5,
)
```

### 柱内数值注释
在柱内或柱上方以 32–36pt 打印精确数字，无需网格即可辨读：
```python
for bar, value in zip(bars, values):
    luminance = compute_luminance(bar_color)
    textcolor = 'white' if luminance < 128 else 'black'
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() - 0.10,
            f'{value:.2f}',
            ha='center', va='bottom',
            fontsize=32, color=textcolor)
```

### 哈希编码（黑白打印安全）
```python
hatches = ['/', '\\', '.', 'x', 'o']
for bar, hatch in zip(bars, hatches):
    bar.set_hatch(hatch)
```

### 误差线样式
```python
error_kw = {
    'elinewidth': 2,
    'capthick': 2,
    'capsize': 15,
}
```

---

## 6) 折线/趋势图

- 线宽：2–3pt，控制透明度。
- 标记大小：8–12pt 圆形。
- 在同一行放置一个共享图例，而非每个轴重复图例。
- 时间渐变透明度：
  ```python
  from matplotlib.collections import LineCollection
  alphas = np.linspace(0.3, 0.9, n_segments)
  # 用逐段 alpha 构建 LineCollection
  ```
- `fill_between` 用于不确定性带（保持 alpha 低：0.1–0.2）。
- 参考基线用虚线水平线：`ax.axhline(y=..., linestyle='--', alpha=0.3, linewidth=4)`。
- 无网格；稀疏 y 轴刻度引导视线。

---

## 7) 热力图规则

```python
import matplotlib as mpl

# 发散型（正/负）：按列方向用红+蓝配色
cmap_pos = plt.cm.Reds
cmap_neg = plt.cm.Blues_r

# 掩盖 NaN 单元格显示为白色
cmap.set_bad(color='white')

# 逐列归一化
norm = mpl.colors.Normalize(vmin=col_min, vmax=col_max)

# 移除边框
ax.set_frame_on(False)

# 移除刻度线，保留标签
ax.tick_params(axis='x', which='both', bottom=False, top=False, length=0)
```

单元格文字对比度：
```python
r, g, b, _ = cmap(norm(value))
luminance = 0.299*r + 0.587*g + 0.114*b
text_color = 'white' if luminance < 0.5 else 'black'
```

---

## 8) 雷达/极坐标图

- 投影：`fig.add_subplot(projection='polar')`。
- 移除默认网格和边框；绘制自定义辐条和轮廓多边形。
- 按基准刻度列表将每个辐条归一化到显示范围（如 45–90）。
- 使用 `ax.set_theta_zero_location('N')` 从顶部开始。
- 图例：`bbox_to_anchor=(1.40, 0.05)` 放在右侧外部。

---

## 9) 导出策略

### SVG 是必需的主格式

SVG 保留可编辑文本（当 `svg.fonttype = 'none'` 时），支持无损缩放，是文本标签需要在 Illustrator 或 Inkscape 中后期对齐的图的必需格式。始终先保存 SVG。

```python
import os
os.makedirs('./figures/', exist_ok=True)
fig.tight_layout(pad=2)   # 默认；紧凑多面板用 pad=1

# ── 主格式 ── 可编辑矢量，文本为 <text> 节点 ─────────────────────────
fig.savefig('./figures/name.svg', bbox_inches='tight')

# ── 次格式 ── 光栅预览/投稿入口 ────────────────
fig.savefig('./figures/name.png', dpi=300, bbox_inches='tight')

plt.close(fig)   # 始终关闭释放内存
```

**DPI 指南（仅 PNG）**：
- `dpi=300` — 所有图类型标准。
- `dpi=600` — 方法众多的密集柱状图。

**永远不要** 使用 `svg.fonttype = 'path'`（matplotlib 默认）：它将字形转换为贝塞尔曲线，破坏文本可编辑性。savefig 前必须设置强制的三行 rcParams（见 api.md）。

---

## 10) 多面板信息架构

### 规则：每个面板必须回答一个独立的科学问题

多面板图中，每个面板应独立可读。覆盖一个面板后，其他面板不应留下无法弥补的信息缺口。

**推荐三级递进**：

| 层级 | 回答的问题 | 典型编码 |
|------|-----------|---------|
| 全景 | "整体格局是什么？" | 堆叠柱状图、组成图 |
| 偏差 | "每组有什么不同？" | Z-score 热力图（发散配色） |
| 关系 | "变量如何共变？" | 散点/气泡图 |

### 反冗余清单

定稿前检查：

- [ ] 面板 b **没有**以不同视觉形式重复面板 a 的数据
- [ ] 面板 c 增加了 a 和 b 缺失的维度（如相关性、数学关系）
- [ ] 每个面板有自己的轴标签词汇（不同的 x/y 量）

### 常见冗余陷阱

| 陷阱 | 示例 | 修复 |
|------|------|------|
| 绝对+绝对 | 堆叠柱状图（%）+ 同一 % 热力图 | 替换热力图为 Z-score 偏差 |
| 父集子集 | 仅肿瘤的排名柱只是堆叠柱的一列 | 替换为散点：肿瘤 % vs 免疫 % |
| 两个排名 | 两个相关指标的排名柱 | 替换一个为散点/气泡 |
| 不同图表同一数据切片 | 饼图+堆叠柱状图 | 合并或替换一个为关系图 |

### Z-score 偏差热力图（组成柱的补充）

面板 a 显示绝对组成时，面板 b 应显示每组的 **异常情况**：

```python
# heat: DataFrame（队列 × 细胞类型类别），值为 %
z = (heat - heat.mean(axis=0)) / heat.std(axis=0)
im = ax.imshow(z.values, cmap="RdBu_r", aspect="auto", vmin=-2.5, vmax=2.5)
# colorbar 标签：
cbar.set_label("Z-score vs pan-cohort mean")
```

用 `RdBu_r`（红 = 高于均值富集，蓝 = 低于均值耗竭）。此发散视图与面板 a 的绝对百分比视图正交。

### 气泡散点图（同时补充两者）

a = 组成，b = 偏差时，面板 c 应揭示 **数学共变关系**：

```python
# x: 主要部分（如肿瘤 %）
# y: 功能读出（如免疫细胞 %）
# size: 第三变量（如基质 %）
ax.scatter(x, y, s=stroma * scale, c=colors,
           edgecolors="white", linewidth=0.8, alpha=0.9)
# 在中位数 x 和中位数 y 处画象限参考线
ax.axvline(np.median(x), lw=1.2, ls="--", color="#767676", alpha=0.6)
ax.axhline(np.median(y), lw=1.2, ls="--", color="#767676", alpha=0.6)
```

用小号灰色文字标注象限（如"高 A/低 B""低 A/高 B"等）。

---

## 11) 反冗余清单（Anti-redundancy checklist）

多面板图定稿前逐条检查。**同一数据用不同图表形式重复展示是审稿人最常见的批评之一。**

### 检查清单

- [ ] 面板 b **不是**用不同视觉形式重复展示面板 a 的相同数据
- [ ] 面板 c 增加了 a 和 b 中**不存在的维度**（如相关性、因果关系、空间分布）
- [ ] 每个面板有**独立的坐标轴词汇**（不同的 x/y 变量或不同的物理含义）
- [ ] 柱状图和折线图不同时展示相同的对比关系——选择最适合论证意图的一种
- [ ] 散点图和折线图不重复——散点看关系，折线看趋势，x 轴含义应不同

### 常见冗余陷阱

| 陷阱 | 示例 | 修正 |
|------|------|------|
| 绝对值 + 绝对值 | 堆叠柱(%) + 相同%的热力图 | 热力图换成 z-score deviation |
| 子集重复 | 排名柱只是堆叠柱中一列的子集 | 换成散点：A% vs B% |
| 两个排名 | 两个指标的排序柱状图 | 把其中一个换成 scatter / bubble |
| 不同图表、相同数据切片 | 饼图 + 堆叠柱 | 合并或替换为关系图 |
| 同趋势不同形式 | 折线(均值) + 柱状(均值) | 只保留一种，另一种换成分布图 |

### 数学建模场景示例

**反面教材**（图型单一）：一道优化题画了 9 张图，全是柱状图——收敛过程用柱状、灵敏度用柱状、方案对比用柱状、Pareto 前沿用柱状……

**正确做法**：

| 论点 | 正确图型 | 为什么不是柱状 |
|------|---------|--------------|
| 目标函数收敛 | 折线（x=迭代） | 柱状暗示离散，收敛是连续过程 |
| Pareto 前沿 | 散点（x=obj1, y=obj2） | 点之间无连续关系，不能用折线 |
| 参数灵敏度 | tornado 图 / 折线 | 需要展示参数变化方向 |
| 多方案对比 | 分组柱状 / 雷达图（≤8维） | 柱状适合，但应搭配雷达图展示多维权衡 |

---

## 12) 复现清单

匹配 Nature 出版标准：

- [ ] **强制首行**：`font.family='sans-serif'`，`font.sans-serif=['Arial','DejaVu Sans','Liberation Sans']`，`svg.fonttype='none'`
- [ ] **保存为 SVG**（主格式）。PNG dpi=300 作为可选光栅预览。
- [ ] 关闭上和右边框；无边框图例
- [ ] 有意识选择图表架构：网格、示意图主导复合、图像板或非对称英雄布局
- [ ] 字号 ≥ 16 基础；大柱状面板 24；大面板轴标签 32–54
- [ ] 折线 linewidth=0.8–1.2，axes.linewidth 匹配，参考线 0.6–0.8
- [ ] 使用蓝-绿-红-中性语义配色
- [ ] 黑色背景仅用于图像板，不用于普通图表
- [ ] 当直接标注或一个图例条更清晰时，省略或共享图例
- [ ] y 轴范围收紧到数据范围（值在 80–95 时不用 0–100）
- [ ] 方法在图例中命名时隐藏 x 轴刻度
- [ ] 图例在专用面板或 `frameon=False`
- [ ] **图型多样**：全文 ≥ 3 种图型，每个面板回答唯一问题（反冗余清单见 §11）
- [ ] savefig 前 `tight_layout(pad=2)`
- [ ] savefig 后 `plt.close(fig)`
