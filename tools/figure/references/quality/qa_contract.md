# 交付前 QA 契约

在最终交付前、修订包前、以及图形包含统计声明时使用本参考。

## 交付前检查清单

| 检查项 | 通过条件 |
|---|---|
| 核心结论 | 存在一句话声明，每个面板映射到它 |
| 原型声明 | 图形已声明原型和面板层级 |
| 最终尺寸 | 单栏约 89mm 或双栏约 183mm，高度不超过目标期刊限制 |
| 文字大小 | 正文/刻度/图注文字在最终尺寸下可读，通常 5-7pt |
| 面板标签 | 小写粗体，靠近左上角，通常 8pt |
| 可编辑文字 | SVG/PDF 文字保持可编辑 |
| 字体 | 使用 Arial/Helvetica/sans-serif 回退 |
| 配色 | 无 rainbow 色图；红绿不是唯一编码；灰度打印可区分 |
| 图例策略 | 优先直接标注或共享图例；无重复冗余图例 |
| 统计 | `n`、重复定义、中心统计量、离散程度、检验、校正和精确比较已记录 |
| 源数据 | 定量面板可追溯到干净的 CSV/TSV/XLSX 或脚本输出 |
| 栅格分辨率 | 照片/显微图足够高分辨率；线图使用矢量 |
| 导出打包 | 脚本、源数据、SVG、PDF、PNG 预览和 QA 说明一起交付 |

## 统计图注最小模板

对每个定量面板，记录：

```text
n 定义：
重复类型（生物学/技术/交叉验证折数）：
中心统计量（均值/中位数）：
离散程度/区间（SD/SEM/95%CI/IQR）：
检验方法：
多重比较校正：
显著性符号定义：
源数据文件：
```

对机器学习/模型图形，额外记录：

```text
训练/验证/测试划分：
种子数或折数：
指标定义：
置信区间或变异性定义：
基线定义：
```

## 自动化源码预检

在最终渲染前运行源码级验证：

```bash
python tools/figure/scripts/validate_figure.py path/to/figure.py
python tools/figure/scripts/validate_figure.py path/to/figure.py --strict
```

预检检查源码语法、字体配置、不安全色图、可编辑文字设置、矢量/栅格导出、
DPI、常见期刊宽度、潜在采样偏差和日志守卫。

将结果视为确定性源码审计，而非图形正确的证据。交付前解决所有 `FAIL`。
审查每个 `WARN`，然后运行选定后端并在最终尺寸下检查实际输出。

## 导出检查

```python
import matplotlib as mpl
mpl.rcParams["svg.fonttype"] = "none"
mpl.rcParams["pdf.fonttype"] = 42
fig.savefig("figure.svg")
fig.savefig("figure.pdf")
fig.savefig("figure.png", dpi=300)
```

导出后打开 SVG/PDF，验证文字可选、标签不重叠、图形在最终打印尺寸下可读。
