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

# ---- 知识库 ----
KNOWLEDGE_DIR = ".harness/knowledge"
KNOWLEDGE_SYNC_FILE = ".harness/knowledge/SYNC.yaml"
KNOWLEDGE_INDEX_FILE = ".harness/knowledge/index.md"
KNOWLEDGE_DOMAINS = ["architecture", "domain", "engineering", "operations", "runway", "private"]
KNOWLEDGE_PROMOTION_ARTIFACT = "19-knowledge-promotion.md"

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

本项目使用 `.harness/` 作为 AI Coding 工程化流程的**唯一事实来源**。

### 铁律

1. **所有涉及源码变更、构建、测试、部署的任务必须走 harness**。唯一例外：纯信息查询。
2. **禁止自行修改 state.json 中的 intent/risk**。这些值由 `bridle new` 指定，AI 不得覆盖。
3. **禁止跳过节点**。Dispatcher 决定的下一个节点必须执行，不得因"简单"而跳过。
4. **禁止越权**。只有 verifier 可标记 G3-G8 门禁；developer 不得把 COMPILE 标为 PASS。

### 每次对话

1. 读取 `.harness/state.json` 和 `.harness/workflow.yaml`
2. 由 `.harness/agents/dispatcher.md` 决定下一个节点和角色
3. 产物写入 `state.phase_dir`，禁止写入 `docs/superpowers`
4. 声称完成前执行 `.harness/evals/gates.yaml` 门禁
5. 门禁失败 → 回退，最多重试 2 次，超过 → BLOCKED

### 无效借口

"小改动"、"用户说快"、"之前做过" 一律无效。源码改动 = 非简单任务。
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
