#!/usr/bin/env python3
"""依赖标准库的论文图文件审计器。"""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
REQUIRED_CATEGORIES = ("raw_", "process_", "result_")


def _png_metadata(path: Path) -> dict:
    width = height = None
    dpi_x = dpi_y = None
    with path.open("rb") as stream:
        if stream.read(8) != PNG_SIGNATURE:
            raise ValueError("不是有效的 PNG 文件")
        while True:
            header = stream.read(8)
            if len(header) != 8:
                break
            length, chunk_type = struct.unpack(">I4s", header)
            data = stream.read(length)
            stream.read(4)
            if chunk_type == b"IHDR":
                width, height = struct.unpack(">II", data[:8])
            elif chunk_type == b"pHYs" and len(data) >= 9:
                pixels_x, pixels_y, unit = struct.unpack(">IIB", data[:9])
                if unit == 1:
                    dpi_x = pixels_x * 0.0254
                    dpi_y = pixels_y * 0.0254
            elif chunk_type == b"IEND":
                break
    if width is None or height is None:
        raise ValueError("PNG 缺少 IHDR")
    metadata = {
        "width_px": width,
        "height_px": height,
        "dpi_x": dpi_x,
        "dpi_y": dpi_y,
    }
    if dpi_x and dpi_y:
        metadata["width_in"] = width / dpi_x
        metadata["height_in"] = height / dpi_y
    return metadata


def _svg_metadata(path: Path) -> dict:
    root = ET.parse(path).getroot()
    elements = list(root.iter())
    text_count = sum(element.tag.rsplit("}", 1)[-1] == "text" for element in elements)
    embedded_raster = any(
        element.tag.rsplit("}", 1)[-1] == "image"
        and "base64" in " ".join(str(value) for value in element.attrib.values()).lower()
        for element in elements
    )
    return {"text_count": text_count, "embedded_raster": embedded_raster}


def audit_figure_directory(
    figures_dir: str | Path,
    *,
    min_dpi: int = 300,
    require_categories: bool = True,
    min_per_category: int = 3,
    questions: tuple[str, ...] = (),
) -> dict:
    if min_per_category < 1:
        raise ValueError("每类候选图最低数量必须大于等于 1")
    normalized_questions = tuple(dict.fromkeys(question.strip().casefold() for question in questions))
    if any(not re.fullmatch(r"q[1-9]\d*", question) for question in normalized_questions):
        raise ValueError("子问题标识必须使用 q1、q2 等格式")
    directory = Path(figures_dir).expanduser().resolve()
    issues: list[dict[str, str]] = []
    files: dict[str, dict] = {}
    if not directory.is_dir():
        return {
            "ok": False,
            "directory": str(directory),
            "questions": list(normalized_questions),
            "files": files,
            "issues": [{"severity": "FAIL", "message": "figures 目录不存在"}],
        }

    candidates = sorted(path for path in directory.iterdir() if path.is_file())
    by_stem: dict[str, set[str]] = {}
    for path in candidates:
        suffix = path.suffix.lower()
        if suffix in {".jpg", ".jpeg"}:
            issues.append({"severity": "FAIL", "message": f"数据图禁止使用 JPEG：{path.name}"})
        if suffix not in {".svg", ".png"}:
            continue
        by_stem.setdefault(path.stem, set()).add(suffix)
        try:
            metadata = _png_metadata(path) if suffix == ".png" else _svg_metadata(path)
        except (OSError, ValueError, ET.ParseError) as exc:
            issues.append({"severity": "FAIL", "message": f"无法解析 {path.name}：{exc}"})
            continue
        files[path.name] = metadata
        if suffix == ".png":
            dpi_values = [metadata["dpi_x"], metadata["dpi_y"]]
            if any(value is None for value in dpi_values):
                issues.append({"severity": "FAIL", "message": f"{path.name} 缺少 DPI 元数据"})
            elif min(dpi_values) + 0.5 < min_dpi:
                issues.append({"severity": "FAIL", "message": f"{path.name} 低于 {min_dpi} DPI"})
        elif metadata["text_count"] == 0:
            issues.append({"severity": "FAIL", "message": f"{path.name} 没有可编辑文本节点"})
        elif metadata["embedded_raster"]:
            issues.append({"severity": "WARN", "message": f"{path.name} 含嵌入位图，请确认确有必要"})

    for stem, suffixes in by_stem.items():
        missing = {".svg", ".png"} - suffixes
        if missing:
            issues.append({
                "severity": "FAIL",
                "message": f"{stem} 缺少配对格式：{', '.join(sorted(missing))}",
            })

    if require_categories:
        for prefix in REQUIRED_CATEGORIES:
            count = sum(stem.startswith(prefix) for stem in by_stem)
            if count < min_per_category:
                issues.append({
                    "severity": "FAIL",
                    "message": (
                        f"{prefix} 类候选图仅 {count} 张，"
                        f"低于每类最低 {min_per_category} 张"
                    ),
                })
        if not normalized_questions:
            issues.append({
                "severity": "FAIL",
                "message": "未提供全部子问题标识；请使用 --questions q1 q2 ...",
            })
        for question in normalized_questions:
            for prefix in REQUIRED_CATEGORIES:
                marker = f"{prefix}{question}_"
                if not any(stem.startswith(marker) for stem in by_stem):
                    issues.append({
                        "severity": "FAIL",
                        "message": f"子问题 {question} 缺少 {prefix} 类候选图",
                    })

    return {
        "ok": not any(item["severity"] == "FAIL" for item in issues),
        "directory": str(directory),
        "questions": list(normalized_questions),
        "files": files,
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="检查三类候选图数量、SVG 可编辑文本和 PNG DPI")
    parser.add_argument("figures_dir", help="PROJECT_ROOT 下的 figures 目录")
    parser.add_argument("--min-dpi", type=int, default=300)
    parser.add_argument("--min-per-category", type=int, default=3, help="每类逻辑候选图最低数量")
    parser.add_argument(
        "--questions",
        nargs="+",
        default=(),
        metavar="Q",
        help="题目全部子问题标识，例如 q1 q2 q3",
    )
    parser.add_argument("--no-category-check", action="store_true", help="仅检查已有图，不要求三类前缀")
    parser.add_argument("--strict", action="store_true", help="存在 FAIL 时返回非零退出码")
    args = parser.parse_args()
    report = audit_figure_directory(
        args.figures_dir,
        min_dpi=args.min_dpi,
        require_categories=not args.no_category_check,
        min_per_category=args.min_per_category,
        questions=tuple(args.questions),
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if args.strict and not report["ok"] else 0


if __name__ == "__main__":
    sys.exit(main())
