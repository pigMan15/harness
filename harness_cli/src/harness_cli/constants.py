"""Bridle 全局常量：配色主题、Schema 版本、路径约定。"""

from pathlib import Path

# ---- 版本兼容 ----
SUPPORTED_SCHEMA_VERSIONS = ["1.0"]

# ---- 路径约定 ----
HARNESS_DIR = ".harness"
STATE_FILE = ".harness/state.json"
WORKFLOW_FILE = ".harness/workflow.yaml"
GATES_FILE = ".harness/evals/gates.yaml"
SCHEMA_FILE = ".harness/state.schema.json"
PHASES_DIR = ".harness/phases"
RUNS_DIR = ".harness/runs"
AGENTS_FILE = "AGENTS.md"
CLAUDE_FILE = "CLAUDE.md"

# ---- 色板：映射到 Rich/Textual 终端 256 色 ----
# 主色 #7C3AED purple  辅助色 #06B6D4 cyan
# 成功 #22C55E green   警告 #EAB308 yellow
# 错误 #EF4444 red     弱化 #71717A dim
THEME = {
    "primary":       "purple",
    "secondary":     "cyan",
    "success":       "green",
    "warning":       "yellow",
    "error":         "red",
    "muted":         "dim",
    "progress_bar":  "purple",
}

# ---- ASCII 启动画面 (80 列) ----
BANNER = r"""
  ╔══════════════════════════════════════════════╗
  ║                                              ║
  ║    ═══╗  ╔═══  ╔═══╗  ╔══╗  ╔══╗  ╔═══╗    ║
  ║     ╔╝  ║     ║   ║  ║      ║  ║  ║         ║
  ║     ║   ╠═══  ╠═══╝  ╠══╗   ║  ║  ╚═══╗     ║
  ║     ║   ║     ║  ╲   ║  ║   ║  ║      ║     ║
  ║    ═╝   ╚═══  ║  ╲╲  ╚══╝   ╚══╝  ╚═══╝     ║
  ║                                              ║
  ║         AI Coding Harness                    ║
  ╚══════════════════════════════════════════════╝
"""

# ---- AGENTS.md / CLAUDE.md 追加标记块 ----
HARNESS_ENTRY_MARKER_START = "<!-- HARNESS-ENTRY:START"
HARNESS_ENTRY_MARKER_END = "<!-- HARNESS-ENTRY:END -->"

HARNESS_ENTRY_BLOCK = """<!-- HARNESS-ENTRY:START — managed by bridle, do not edit manually -->
## AI Coding Harness

本项目使用 `.harness/` 作为 AI Coding 工程化流程。

开始非简单任务前：
1. 读取 `.harness/state.json`
2. 读取 `.harness/workflow.yaml`
3. 使用 `.harness/agents/dispatcher.md` 判断下一步
4. 阶段产物写入 `state.phase_dir`
5. 完成前按 `.harness/evals/gates.yaml` 执行门禁
6. 高风险、重构或架构/接口契约变化时，先生成 `10-coding-design.md` 并让用户确认

写入前必须先判断产物类型：源码写入目标源码仓库；流程产物只写入当前 `state.phase_dir`。
<!-- HARNESS-ENTRY:END -->
"""

# ---- 必需文件清单（validate 检查） ----
REQUIRED_FILES = [
    ".harness/state.json",
    ".harness/state.schema.json",
    ".harness/workflow.yaml",
    ".harness/evals/gates.yaml",
    ".harness/runs/.gitkeep",
    ".harness/agents/dispatcher.md",
    ".harness/agents/developer.md",
    ".harness/agents/verifier.md",
    ".harness/rules/artifact-location.md",
    ".harness/rules/build.md",
    ".harness/rules/safety.md",
    ".harness/rules/evidence.md",
    ".harness/phases/.gitkeep",
]
