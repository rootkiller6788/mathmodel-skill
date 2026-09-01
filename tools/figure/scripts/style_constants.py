#!/usr/bin/env python3
"""可复用的绘图常量与工具函数。

从原 plot_style.py 提取，供 tools/figure/ 下各脚本和外部代码共用。
布局审计和导出功能由 visual_qa.py 和 export_figure.py 替代。
"""

from __future__ import annotations

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
# 色盲安全配色（以色觉可达性为先，颜色名称表达用途而不是绑定具体模型）
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


__all__ = [
    "COLOR_SEQUENCE",
    "PALETTE",
    "WIDTHS_IN",
    "SKILL_ROOT",
    "add_panel_labels",
    "choose_font",
    "figure_size",
    "publication_subplots",
    "resolve_output_stem",
]
