#!/usr/bin/env python3
"""数学建模论文图的统一样式工具（向后兼容层）。

本文件保留原有 API 以兼容 ``from utils.plot_style import ...`` 的外部代码。
实际常量和工具函数已迁移到 tools/figure/scripts/style_constants.py。
布局审计和导出功能由 tools/figure/scripts/visual_qa.py 和
tools/figure/scripts/export_figure.py 替代。
"""

from __future__ import annotations

import logging
import unicodedata
import warnings
from pathlib import Path
from typing import Sequence


# ---------------------------------------------------------------------------
# SKILL_ROOT 定位
# ---------------------------------------------------------------------------

def _is_math_modeling_skill_root(path: Path) -> bool:
    return (
        (path / "SKILL.md").is_file()
        and (path / "VERSION").is_file()
        and (
            path
            / "references"
            / "roles"
            / "编程手"
            / "scripts"
            / "plot_style.py"
        ).is_file()
    )


def _find_skill_root(path: Path) -> Path | None:
    directory = path.resolve().parent
    return next(
        (candidate for candidate in (directory, *directory.parents)
         if _is_math_modeling_skill_root(candidate)),
        None,
    )


SKILL_ROOT = _find_skill_root(Path(__file__))

# ---------------------------------------------------------------------------
# 色盲安全配色
# ---------------------------------------------------------------------------

PALETTE = {
    "primary": "#0072B2",
    "secondary": "#E69F00",
    "positive": "#009E73",
    "contrast": "#D55E00",
    "accent": "#CC79A7",
    "sky": "#56B4E9",
    "neutral": "#6B7280",
    "dark": "#222222",
}

COLOR_SEQUENCE = tuple(PALETTE[name] for name in (
    "primary",
    "secondary",
    "positive",
    "contrast",
    "accent",
    "sky",
    "neutral",
))

# ---------------------------------------------------------------------------
# 论文栏宽（英寸）
# ---------------------------------------------------------------------------

WIDTHS_IN = {
    "single": 3.5,
    "double": 7.2,
    "report": 6.3,
}

# ---------------------------------------------------------------------------
# 字体选择
# ---------------------------------------------------------------------------

_CJK_SANS = (
    "Noto Sans CJK SC",
    "Source Han Sans SC",
    "Microsoft YaHei",
    "SimHei",
    "PingFang SC",
)


def _available_fonts() -> set[str]:
    from matplotlib import font_manager
    return {item.name for item in font_manager.fontManager.ttflist}


def choose_font(language: str = "zh") -> str:
    """选择可用字体；中文字体缺失时给出警告并安全回退。"""
    if language not in {"zh", "en"}:
        raise ValueError("language 只能是 'zh' 或 'en'")
    available = _available_fonts()
    if language == "zh":
        for name in _CJK_SANS:
            if name in available:
                return name
        warnings.warn(
            "未检测到常用中文字体，已回退到 DejaVu Sans；导出前必须检查中文和特殊符号是否缺字。",
            RuntimeWarning,
            stacklevel=2,
        )
    for name in ("Arial", "Helvetica", "DejaVu Sans"):
        if name in available:
            return name
    return "DejaVu Sans"


# ---------------------------------------------------------------------------
# 尺寸计算
# ---------------------------------------------------------------------------

def figure_size(width: str = "report", aspect: float = 0.62) -> tuple[float, float]:
    """按最终使用宽度返回英寸尺寸，避免在论文中二次大幅缩放。"""
    if width not in WIDTHS_IN:
        raise ValueError(f"未知宽度方案: {width}")
    if aspect <= 0:
        raise ValueError("aspect 必须大于 0")
    width_in = WIDTHS_IN[width]
    return width_in, width_in * aspect


# ---------------------------------------------------------------------------
# 子图创建
# ---------------------------------------------------------------------------

def publication_subplots(
    nrows: int = 1,
    ncols: int = 1,
    *,
    width: str = "report",
    aspect: float = 0.62,
    width_ratios: Sequence[float] | None = None,
    height_ratios: Sequence[float] | None = None,
    squeeze: bool = True,
):
    """按最终尺寸创建子图，并允许显式声明主次面板比例。"""
    import matplotlib.pyplot as plt

    if nrows < 1 or ncols < 1:
        raise ValueError("nrows 和 ncols 必须大于 0")
    if width_ratios is not None and len(width_ratios) != ncols:
        raise ValueError("width_ratios 数量必须与 ncols 一致")
    if height_ratios is not None and len(height_ratios) != nrows:
        raise ValueError("height_ratios 数量必须与 nrows 一致")
    gridspec_kw = {}
    if width_ratios is not None:
        gridspec_kw["width_ratios"] = list(width_ratios)
    if height_ratios is not None:
        gridspec_kw["height_ratios"] = list(height_ratios)
    return plt.subplots(
        nrows,
        ncols,
        figsize=figure_size(width, aspect),
        layout="constrained",
        gridspec_kw=gridspec_kw or None,
        squeeze=squeeze,
    )


# ---------------------------------------------------------------------------
# 面板标签
# ---------------------------------------------------------------------------

from collections.abc import Iterable as _Iterable


def add_panel_labels(
    axes: _Iterable,
    labels: Sequence[str] | None = None,
    *,
    x_offset_pt: float = -8.0,
    y_offset_pt: float = 1.0,
) -> None:
    """在各面板左上外侧添加小写粗体编号。"""
    axes_list = list(axes)
    panel_labels = list(labels) if labels is not None else [chr(97 + i) for i in range(len(axes_list))]
    if len(panel_labels) != len(axes_list):
        raise ValueError("labels 数量必须与 axes 数量一致")
    for axis, label in zip(axes_list, panel_labels):
        axis.annotate(
            label,
            xy=(0, 1),
            xycoords="axes fraction",
            xytext=(x_offset_pt, y_offset_pt),
            textcoords="offset points",
            ha="right",
            va="bottom",
            fontsize=8,
            fontweight="bold",
            annotation_clip=False,
        )


# ---------------------------------------------------------------------------
# 路径安全
# ---------------------------------------------------------------------------

def resolve_output_stem(output_stem: str | Path) -> Path:
    """解析导出路径，并禁止把任务产物写回 Skill 目录。"""
    stem = Path(output_stem).expanduser().resolve()
    if stem.suffix.lower() in {".svg", ".png", ".pdf"}:
        stem = stem.with_suffix("")
    if any(
        _is_math_modeling_skill_root(candidate)
        for candidate in (stem.parent, *stem.parent.parents)
    ):
        raise ValueError("图形产物必须写入 PROJECT_ROOT，不能写入 SKILL_ROOT")
    return stem


# ---------------------------------------------------------------------------
# 向后兼容：已被 tools/figure/ 新工具替代的函数
# 以下函数保留以兼容现有测试和外部代码。新代码请使用
# tools/figure/scripts/ 下的 setup_style、visual_qa、export_figure。
# ---------------------------------------------------------------------------

def apply_publication_style(language: str = "zh", width: str = "report") -> dict:
    """应用出版样式基线（向后兼容）。新代码请用 setup_style()。"""
    import matplotlib as mpl
    from cycler import cycler

    font_name = choose_font(language)
    size = figure_size(width)
    mpl.rcParams.update({
        "figure.figsize": size,
        "figure.constrained_layout.use": True,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "font.family": "sans-serif",
        "font.sans-serif": [font_name, "Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 7.5,
        "axes.titlesize": 8.0,
        "axes.titleweight": "normal",
        "axes.titlelocation": "left",
        "axes.titlepad": 4.0,
        "axes.labelsize": 8.0,
        "xtick.labelsize": 7.0,
        "ytick.labelsize": 7.0,
        "legend.fontsize": 7.0,
        "axes.linewidth": 0.7,
        "lines.linewidth": 1.1,
        "lines.markersize": 3.5,
        "patch.linewidth": 0.6,
        "hatch.linewidth": 0.4,
        "xtick.major.size": 3.0,
        "ytick.major.size": 3.0,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": False,
        "legend.frameon": False,
        "legend.handlelength": 1.6,
        "legend.borderaxespad": 0.4,
        "axes.unicode_minus": False,
        "axes.prop_cycle": cycler(color=COLOR_SEQUENCE),
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "savefig.facecolor": "white",
        "savefig.dpi": 300,
    })
    return {"font": font_name, "size_inches": size, "colors": COLOR_SEQUENCE}


class _GlyphHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.messages: list[str] = []

    def emit(self, record) -> None:
        message = record.getMessage()
        if "Glyph" in message and "missing from font" in message:
            self.messages.append(message)


def _labels_overlap(labels, renderer, axis: str) -> bool:
    boxes = [
        label.get_window_extent(renderer)
        for label in labels
        if label.get_visible() and label.get_text().strip()
    ]
    boxes.sort(key=(lambda box: box.x0) if axis == "x" else (lambda box: box.y0))
    if axis == "x":
        return any(left.x1 > right.x0 + 1 for left, right in zip(boxes, boxes[1:]))
    return any(lower.y1 > upper.y0 + 1 for lower, upper in zip(boxes, boxes[1:]))


def audit_layout(fig) -> list[str]:
    """在导出前检查缺字、画布外文字和相邻刻度重叠（向后兼容）。"""
    import matplotlib.text as mtext

    handler = _GlyphHandler()
    logger = logging.getLogger("matplotlib")
    logger.addHandler(handler)
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            fig.canvas.draw()
    finally:
        logger.removeHandler(handler)

    messages = handler.messages + [
        str(item.message)
        for item in caught
        if "Glyph" in str(item.message) and "missing from font" in str(item.message)
    ]
    issues = [f"缺字：{message}" for message in dict.fromkeys(messages)]
    renderer = fig.canvas.get_renderer()
    width, height = fig.bbox.width, fig.bbox.height
    tick_ids = {
        id(label)
        for axis in fig.axes
        for label in (*axis.get_xticklabels(), *axis.get_yticklabels())
    }
    clipped = []
    for text in fig.findobj(mtext.Text):
        if id(text) in tick_ids or not text.get_visible() or not text.get_text().strip():
            continue
        box = text.get_window_extent(renderer)
        if box.x0 < -1 or box.y0 < -1 or box.x1 > width + 1 or box.y1 > height + 1:
            clipped.append(text.get_text().replace("\n", " ")[:24])
    if clipped:
        issues.append("文字可能超出画布：" + "、".join(dict.fromkeys(clipped)))
    for index, axis in enumerate(fig.axes, start=1):
        if _labels_overlap(axis.get_xticklabels(), renderer, "x"):
            issues.append(f"第 {index} 个坐标轴的 x 刻度标签重叠")
        if _labels_overlap(axis.get_yticklabels(), renderer, "y"):
            issues.append(f"第 {index} 个坐标轴的 y 刻度标签重叠")
    return issues


def _display_width(text: str) -> int:
    return sum(
        2 if unicodedata.east_asian_width(character) in {"W", "F"} else 1
        for character in text
    )


def _is_colorbar_axis(axis) -> bool:
    return axis.get_label() == "<colorbar>" or hasattr(axis, "_colorbar")


def audit_design(fig) -> list[str]:
    """检查可由对象结构确定的高风险设计（向后兼容）。"""
    from matplotlib.container import BarContainer

    issues: list[str] = []
    data_axes = [axis for axis in fig.axes if not _is_colorbar_axis(axis)]
    colorbar_axes = [axis for axis in fig.axes if _is_colorbar_axis(axis)]
    colorbar_mappables = {
        id(axis._colorbar.mappable)
        for axis in colorbar_axes
        if hasattr(axis, "_colorbar") and getattr(axis._colorbar, "mappable", None) is not None
    }
    for index, axis in enumerate(data_axes, start=1):
        for location in ("left", "center", "right"):
            title = axis.get_title(loc=location).strip()
            title_lines = title.splitlines()
            if title and (
                len(title_lines) > 1
                or max(_display_width(line) for line in title_lines) > 28
            ):
                issues.append(
                    f"第 {index} 个坐标轴标题过长；完整论述应移到图注，面板内只保留短标题"
                )
                break

        legend = axis.get_legend()
        if legend is not None and len(legend.get_texts()) > 5:
            issues.append(
                f"第 {index} 个坐标轴图例超过 5 项；应直接标注、改为共享图例或拆分证据"
            )

        for line in axis.lines:
            marker = line.get_marker()
            if marker in {None, "", " ", "None", "none"}:
                continue
            point_count = len(line.get_xdata(orig=False))
            if point_count > 25 and line.get_markevery() is None:
                issues.append(
                    f"第 {index} 个坐标轴对 {point_count} 个点逐点绘制标记；"
                    "应取消标记或设置 markevery"
                )
                break

        for container in axis.containers:
            if not isinstance(container, BarContainer) or not container.patches:
                continue
            if container.orientation == "vertical":
                lower, upper = axis.get_ylim()
            else:
                lower, upper = axis.get_xlim()
            tolerance = max(abs(upper - lower), 1.0) * 1e-9
            if lower > tolerance or upper < -tolerance:
                issues.append(
                    f"第 {index} 个坐标轴的柱状图未从零开始；"
                    "若必须截断，应改用点图/区间图并显式说明"
                )
                break

        for image in axis.images:
            values = image.get_array()
            if (
                getattr(values, "size", 0) <= 4
                and len(axis.texts) >= getattr(values, "size", 0)
                and id(image) in colorbar_mappables
            ):
                issues.append(
                    f"第 {index} 个坐标轴是已标数值的 2×2 小矩阵，"
                    "不应再使用冗余 colorbar"
                )
                break
    for legend in fig.legends:
        if len(legend.get_texts()) > 5:
            issues.append("整图共享图例超过 5 项；应直接标注、拆分证据或突出核心系列")
            break
    return issues


def _save_grayscale_preview(png_path: Path, dpi: int) -> Path:
    import matplotlib.image as image_io
    import numpy as np

    pixels = image_io.imread(png_path)
    rgb = pixels[..., :3]
    if pixels.shape[-1] == 4:
        alpha = pixels[..., 3:4]
        rgb = rgb * alpha + (1 - alpha)
    grayscale = np.dot(rgb, (0.2126, 0.7152, 0.0722))
    output = png_path.parent / "_qa" / f"{png_path.stem}_grayscale.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    image_io.imsave(output, grayscale, cmap="gray", vmin=0, vmax=1, dpi=dpi)
    return output


def export_figure(
    fig,
    output_stem: str | Path,
    *,
    dpi: int = 300,
    grayscale_preview: bool = True,
    strict_layout: bool = True,
    strict_design: bool = True,
) -> dict[str, str]:
    """按固定物理尺寸导出（向后兼容）。新代码请用 tools/figure/scripts/export_figure.py。"""
    if dpi < 300:
        raise ValueError("论文图 PNG 的 dpi 不能低于 300")
    layout_issues = audit_layout(fig)
    if strict_layout and layout_issues:
        raise ValueError("版面预检未通过：" + "；".join(layout_issues))
    design_issues = audit_design(fig)
    if strict_design and design_issues:
        raise ValueError("出版设计预检未通过：" + "；".join(design_issues))
    stem = resolve_output_stem(output_stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    svg_path = stem.with_suffix(".svg")
    png_path = stem.with_suffix(".png")
    fig.savefig(svg_path)
    fig.savefig(png_path, dpi=dpi)
    outputs = {"svg": str(svg_path), "png": str(png_path)}
    if grayscale_preview:
        outputs["grayscale"] = str(_save_grayscale_preview(png_path, dpi))
    return outputs


__all__ = [
    "COLOR_SEQUENCE",
    "PALETTE",
    "WIDTHS_IN",
    "SKILL_ROOT",
    "add_panel_labels",
    "apply_publication_style",
    "audit_design",
    "audit_layout",
    "choose_font",
    "export_figure",
    "figure_size",
    "publication_subplots",
    "resolve_output_stem",
]
