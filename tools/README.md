# tools/ 子工具链

六个领域工具，供论文/求解流程按需调用。每个子目录自带 `SKILL.md` 作为工具手册（含使用协议与场景触发），`scripts/` 为具体脚本。SKILL.md 顶部 frontmatter 的 `name`/`description` 即工具入口标识。

| 工具 | 目录 | 主要用途 | 入口 |
|---|---|---|---|
| 可视化 | `figure/` | 数据剖析 → 选图 → 出版级成图（Nature/IEEE/中文核心级别），三类图体系与自检闭环 | `figure/SKILL.md` |
| 论文搜索 | `paper_search/` | OpenAlex + AnySearch 双引擎并行检索与交叉核验 | `paper_search/SKILL.md` |
| DOCX | `docx/` | 创建/编辑/校验 Word；LaTeX→DOCX 转换、原生公式、三线表、修订批注 | `docx/SKILL.md` |
| Excel | `xlsx/` | 读取/创建/修改/验证 XLSX；模板保留、公式重算、错误检查 | `xlsx/SKILL.md` |
| PDF | `pdf/` | 读/合并/拆分/加水印/填表/加密/OCR 等 PDF 操作 | `pdf/SKILL.md` |
| LaTeX | `latex/` | 用官方或内置模板创建、编译、校验 LaTeX 论文项目 | `latex/SKILL.md` |

## 在竞赛流程中的触发点

- 编程手 Stage 5/6 出图 → `figure`；读取附件数据 → `xlsx`（Excel）/ `pdf`（PDF 题面与附件）。
- 论文手 Stage 8 默认走 `templates/latex/<comp>` 主渲染链（`scripts/render_paper.py`）；用户显式要求 Word 时经 `tools/docx` 降级路径。
- LaTeX 预检/关键词/匿名检查脚本统一在根 `scripts/latex_check/`，与 `tools/latex` 的编译能力配合使用。

## 模板树说明（避免改错）

- **主渲染树**是 `templates/latex/<comp>/main.tex`——`scripts/render_paper.py` 只认这一棵。
- `latex/assets/templates/` 是 `tools/latex` 子工具自带的示例镜像，**不是**主渲染路径。修改主树模板后若需子工具一致，请手动同步。
- `latex-alt/`（含 `cumcmthesis.cls` 兼容类）为可选降级模板，非默认。

## 许可提示

各子工具保留各自的 `LICENSE`（如 `docx/`、`xlsx/`、`pdf/` 下的 `LICENSE.txt`）。`pdf/SKILL.md` frontmatter 声明其 `license: Proprietary`，使用前请以该目录内 `LICENSE.txt` 的完整条款为准；其余内容按根仓库 `LICENSE` 与 `THIRD_PARTY_NOTICES.md` 处理。
