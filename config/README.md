# config/ 配置说明

当前只有一份运行时权重配置：`dim_weights.json`。

## `dim_weights.json` — L1 评分维度权重

`score_artifact.py` 在 `compute_verdict` 前，把各阶段各维度的 L1 打分按题型的权重重加权，得到 `weighted_mean = Σ(sᵢ·wᵢ)/Σwᵢ`。结构与编辑规则如下：

```jsonc
{
  "cumcm": {                       // 竞赛代码: cumcm | mcm | diangong
    "default": {                   // 题型兜底（等价老逻辑的全 1.0）
      "_note": "全 1.0, 等价老逻辑"
    },
    "A_optimization": {            // 具体题型
      "_note": "…说明为何加权…",
      "3": {"1_candidate_diversity": 1.2},   // stage → dim → 权重
      "5": {"1_subproblem_completeness": 1.0}
    }
  }
}
```

- **未列出的 stage/dim 默认 1.0**；`task_type=default` 与老逻辑等价。
- 权重被 **clamp 到 `[0.7, 1.5]`**；加权后维度分数仍落在 `[1, 10]`。
- 顶层 `_doc` / `_design` / `_clamp` 只作说明，校验脚本会读取 `_clamp`。
- 题型键应尽量与 `competitions/<comp>/topic_specs.json` 的 task_type 命名一致；不一致的题型不会命中权重，落到 `default`。改名前先确认两处与 `score_artifact.py` 的匹配逻辑。

## 维护约定

- 修改维度权重会影响最终 verdict（`raw_min` / `weighted_mean`），属于行为变更：需同时更新 `references/feedback_layer1_critic.md`、`references/rubrics.md` 与 `scripts/score_artifact.py` 中一致的定义，并补充测试 fixture。
- 具体见根 `SKILL.md`「收敛准则」与 `AGENTS.md`。
