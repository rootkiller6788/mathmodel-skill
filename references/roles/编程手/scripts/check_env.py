#!/usr/bin/env python3
"""按选中的模型功能动态检查 Python 依赖。"""

import argparse
import importlib.metadata
import importlib.util
import json
import sys


FEATURES = {
    "data": [("numpy", "numpy"), ("pandas", "pandas")],
    "visualization": [("matplotlib", "matplotlib")],
    "excel": [("openpyxl", "openpyxl")],
    "optimization": [("scipy", "scipy")],
    "integer-optimization": [("pulp", "pulp|ortools")],
    "statistics": [("scipy", "scipy"), ("statsmodels", "statsmodels")],
    "machine-learning": [("sklearn", "scikit-learn")],
    "time-series": [("statsmodels", "statsmodels")],
    "graph": [("networkx", "networkx")],
    "image": [("PIL", "pillow")],
}


def _module_exists(module: str) -> bool:
    try:
        return importlib.util.find_spec(module) is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        return False


def check_features(features):
    unknown = sorted(set(features) - FEATURES.keys())
    if unknown:
        raise ValueError("未知功能: " + ", ".join(unknown))

    required = []
    for feature in features:
        for item in FEATURES[feature]:
            if item not in required:
                required.append(item)

    installed = {}
    missing = []
    for module, package in required:
        alternatives = package.split("|")
        if "|" in package:
            alternative_modules = [module] + alternatives[1:]
            found_module = next((name for name in alternative_modules if _module_exists(name)), None)
            if not found_module:
                missing.append(package)
                continue
            module = found_module
            package = "pulp" if module == "pulp" else "ortools"
        elif not _module_exists(module):
            missing.append(package)
            continue
        try:
            installed[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            installed[package] = "已安装（版本未知）"

    return {
        "ok": not missing,
        "features": list(features),
        "python": sys.version.split()[0],
        "installed": installed,
        "missing": missing,
        "install_command": "python -m pip install " + " ".join(missing) if missing else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="按模型功能检查 Python 依赖")
    parser.add_argument("--features", nargs="+", required=True, choices=sorted(FEATURES))
    args = parser.parse_args()
    report = check_features(args.features)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
