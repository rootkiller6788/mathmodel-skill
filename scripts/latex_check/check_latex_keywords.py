#!/usr/bin/env python3
r"""Check that mathematical modeling paper keywords are modeling terms.

The check is intentionally conservative for CUMCM-style submissions: keywords
should be model/method/algorithm/evaluation terms instead of problem objects or
industry background words. It supports \keywords{...}, Chinese "关键词：...",
and mcmthesis \begin{keywords}...\end{keywords}.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Common terms appearing in mathematical-modeling textbooks, courses, and contest papers.
# A keyword passes if it contains one of these terms or matches an English equivalent.
MODELING_TERMS_CN = [
    "数学建模", "优化模型", "规划模型", "线性规划", "非线性规划", "整数规划", "混合整数规划", "0-1规划", "目标规划",
    "动态规划", "随机规划", "鲁棒优化", "多目标优化", "组合优化", "最优化", "优化", "约束优化",
    "回归分析", "线性回归", "多元回归", "逻辑回归", "逐步回归", "岭回归", "Lasso回归", "非参数回归",
    "时间序列", "ARIMA", "灰色预测", "灰色模型", "GM", "马尔可夫", "马尔可夫链", "预测模型",
    "聚类分析", "K-means", "层次聚类", "分类模型", "判别分析", "主成分分析", "因子分析", "降维",
    "层次分析法", "熵权法", "TOPSIS", "模糊综合评价", "综合评价", "评价模型", "指标体系",
    "蒙特卡洛模拟", "仿真", "模拟退火", "遗传算法", "粒子群算法", "蚁群算法", "启发式算法", "差分进化",
    "网络流", "最短路", "图论", "排队论", "博弈论", "元胞自动机", "系统动力学",
    "风险决策", "风险度量", "CVaR", "机会约束", "情景分析", "情景模拟", "灵敏度分析", "敏感性分析", "鲁棒性分析",
    "误差分析", "残差分析", "显著性检验", "假设检验", "相关性分析", "协方差", "概率模型", "贝叶斯", "统计检验",
    "插值", "拟合", "最小二乘", "参数估计", "数据预处理", "标准化", "归一化", "可行性检验",
]

MODELING_TERMS_EN = [
    "mathematical modeling", "optimization", "linear programming", "integer programming", "mixed integer programming",
    "nonlinear programming", "goal programming", "dynamic programming", "robust optimization", "multi-objective optimization",
    "simulation", "monte carlo", "sensitivity analysis", "robustness analysis", "regression", "clustering",
    "principal component analysis", "pca", "time series", "markov", "bayesian", "graph theory", "network flow",
    "shortest path", "queuing", "game theory", "decision analysis", "risk decision", "evaluation model",
    "topsis", "ahp", "entropy weight", "genetic algorithm", "particle swarm", "simulated annealing",
]

# Domain/background words often seen in problem titles. They are not automatically
# forbidden when paired with a modeling method, but a keyword made only from these
# terms should be revised.
DOMAIN_ONLY_HINTS = [
    "农作物", "种植策略", "乡村", "农业", "蔬菜", "销售", "定价", "生产", "企业", "供应链", "交通", "道路",
    "高校", "学生", "运动", "体测", "玻璃", "文物", "矿井", "逃生", "水沙", "黄河", "波浪", "烟幕", "无人机",
    "问题研究", "研究", "策略", "方案", "影响因素", "数据", "方法", "分析", "评价", "预测", "模型",
]

COMMENT_RE = re.compile(r"(?<!\\)%.*")


def strip_comments(text: str) -> str:
    return "\n".join(COMMENT_RE.sub("", line) for line in text.splitlines())


def extract_keywords(text: str) -> list[str]:
    text = strip_comments(text)
    blocks: list[str] = []
    # CUMCM cumcmthesis compatibility command.
    blocks.extend(re.findall(r"\\keywords\{([^{}]+)\}", text, flags=re.DOTALL))
    # MCM mcmthesis environment.
    blocks.extend(re.findall(r"\\begin\{keywords\}(.*?)\\end\{keywords\}", text, flags=re.DOTALL))
    # ctexart fallback Chinese abstract line. Stop at paragraph/line break.
    for m in re.finditer(r"关键词\s*[:：]\s*(.+)", text):
        line = m.group(1).split("\\par")[0].split("\n")[0]
        blocks.append(line)
    if not blocks:
        return []
    raw = "\n".join(blocks)
    raw = re.sub(r"\\quad|\\qquad|;|；|,|，|、|\n", "|", raw)
    raw = re.sub(r"\\textbf\{([^{}]+)\}", r"\1", raw)
    raw = re.sub(r"\\[a-zA-Z]+", "", raw)
    raw = raw.replace("{", "").replace("}", "")
    return [x.strip() for x in raw.split("|") if x.strip()]


def is_modeling_keyword(keyword: str) -> bool:
    compact = re.sub(r"\s+", "", keyword)
    lower = keyword.lower().strip()
    # Direct term match/containment for Chinese. Sorting by length is not necessary, but avoids surprises.
    if any(term and term in compact for term in MODELING_TERMS_CN):
        return True
    if any(term in lower for term in MODELING_TERMS_EN):
        return True
    return False


def has_domain_only_hint(keyword: str) -> bool:
    compact = re.sub(r"\s+", "", keyword)
    return any(hint in compact for hint in DOMAIN_ONLY_HINTS)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tex", help="Main .tex file")
    parser.add_argument("--min-count", type=int, default=3, help="Minimum number of keywords expected")
    parser.add_argument("--max-count", type=int, default=6, help="Maximum number of keywords expected")
    parser.add_argument("--warn-only", action="store_true", help="Warn instead of failing when suspicious keywords are found")
    args = parser.parse_args()

    tex_path = Path(args.tex).resolve()
    if not tex_path.exists():
        print(f"ERROR: tex file not found: {tex_path}")
        return 2
    keywords = extract_keywords(tex_path.read_text(encoding="utf-8"))
    if not keywords:
        print("FAILED: no keywords found. Add \\keywords{...} or a 关键词 line.")
        return 0 if args.warn_only else 1

    problems: list[str] = []
    if len(keywords) < args.min_count:
        problems.append(f"too few keywords: {len(keywords)} < {args.min_count}")
    if len(keywords) > args.max_count:
        problems.append(f"too many keywords: {len(keywords)} > {args.max_count}")

    bad = [kw for kw in keywords if not is_modeling_keyword(kw)]
    domain_only = [kw for kw in keywords if (kw in bad and has_domain_only_hint(kw))]

    if bad:
        problems.append("non-modeling or overly domain-specific keywords: " + ", ".join(bad))
    if domain_only:
        problems.append("replace domain/background keywords with modeling terms, e.g. 混合整数规划, 目标规划, 蒙特卡洛模拟, 风险决策, 敏感性分析")

    if problems:
        for p in problems:
            print("WARNING:" if args.warn_only else "FAILED:", p)
        print("Detected keywords: " + ", ".join(keywords))
        return 0 if args.warn_only else 1

    print(f"PASSED: {len(keywords)} modeling keywords checked: " + ", ".join(keywords))
    return 0


if __name__ == "__main__":
    sys.exit(main())
