# Harness Lightweight Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不增加脚本和目录的前提下，消除流程规则冲突、建立确定性失败恢复，并让现有校验入口发现引用和状态错误。

**Architecture:** `workflow.yaml` 继续作为流程语义来源，`dispatcher` 和 `verifier` 负责执行恢复策略；PowerShell 和 Shell 校验器分别对同一组确定性信号做本地检查，CMD 继续复用 PowerShell。所有实现保持无第三方依赖、只读校验和失败关闭。

**Tech Stack:** YAML 配置、Markdown 规则、PowerShell 5+、POSIX shell、可选 Python 3。

---

## 文件映射

- 修改 `.harness/workflow.yaml`：收窄部署硬规则，增加门禁回退与重试策略。
- 修改 `.harness/agents/dispatcher.md`：按回退映射选择节点，达到上限后阻塞。
- 修改 `.harness/agents/verifier.md`：失败时累计门禁重试并交回 dispatcher。
- 修改 `.harness/state.schema.json`：允许可选的 `retry_counts` 状态。
- 修改 `.harness/evals/runbook.md`：同步失败恢复操作说明。
- 修改 `.harness/scripts/validate-harness.ps1`：实现完整确定性检查。
- 修改 `.harness/scripts/validate-harness.sh`：实现相同核心检查；没有 Python 时明确降级。
- 不修改 `.harness/scripts/validate-harness.cmd`：继续包装 PowerShell。

### Task 1: 统一 workflow 与恢复语义

**Files:**
- Modify: `.harness/workflow.yaml`
- Modify: `.harness/state.schema.json`
- Modify: `.harness/agents/dispatcher.md`
- Modify: `.harness/agents/verifier.md`
- Modify: `.harness/evals/runbook.md`

- [ ] **Step 1: 记录当前冲突基线**

Run:

```powershell
rg -n "business_code_changed_requires|failure_recovery|retry_counts" .harness/workflow.yaml .harness/state.schema.json .harness/agents .harness/evals/runbook.md
```

Expected: 找到 `business_code_changed_requires`，找不到完整的 `failure_recovery` 和 `retry_counts` 定义。

- [ ] **Step 2: 修改 workflow 硬规则和恢复策略**

将 `business_code_changed_requires` 替换为：

```yaml
  high_risk_or_deployment_requires:
    - PRERELEASE_DEPLOYMENT
    - INTERFACE_TEST
```

在 `hard_rules` 后增加：

```yaml
failure_recovery:
  max_auto_retries_per_gate: 2
  gate_to_node:
    G1_REQUIREMENTS: REQUIREMENT_REVIEW
    G2_DESIGN: SOLUTION_DESIGN
    G3_COMPILE: DEVELOPMENT
    G4_UNIT_TEST: DEVELOPMENT
    G5_ATDD: DEVELOPMENT
    G6_EVIDENCE: EVIDENCE_CAPTURE
    G7_PRERELEASE: PRERELEASE_DEPLOYMENT
    G8_ACCEPTANCE: ACCEPTANCE_REPORT
```

- [ ] **Step 3: 扩展可选状态字段**

在 `.harness/state.schema.json` 的 `properties` 中增加：

```json
"retry_counts": {
  "type": "object",
  "additionalProperties": {
    "type": "integer",
    "minimum": 0
  }
}
```

该字段保持可选；旧 run 缺失时按空对象处理，避免要求修改所有初始化脚本。

- [ ] **Step 4: 更新 dispatcher 和 verifier 行为**

明确以下规则：

```text
门禁失败 -> retry_counts[gate] 加 1 -> dispatcher 查询 gate_to_node
次数 <= 2 -> 路由到对应节点
次数 > 2 -> status=BLOCKED，并将门禁和原因写入 blocked_by
门禁通过 -> 对应 retry_counts[gate] 清零或删除
```

Verifier 只记录结果和更新状态，不直接实现修复；dispatcher 只路由，不把失败改成 PASS。

- [ ] **Step 5: 同步门禁运行手册**

在 `.harness/evals/runbook.md` 写明逐门禁回退表、两次自动重试上限和超过上限后的阻塞行为。

- [ ] **Step 6: 做配置静态检查**

Run:

```powershell
Get-Content .harness/state.schema.json -Raw | ConvertFrom-Json | Out-Null
rg -n "high_risk_or_deployment_requires|failure_recovery|max_auto_retries_per_gate|retry_counts" .harness/workflow.yaml .harness/state.schema.json .harness/agents .harness/evals/runbook.md
```

Expected: JSON 解析成功，所有新语义均能定位，不再存在 `business_code_changed_requires`。

### Task 2: 增强 PowerShell 校验器

**Files:**
- Modify: `.harness/scripts/validate-harness.ps1`

- [ ] **Step 1: 提取只读检查函数**

在现有脚本中加入职责单一的函数：

```powershell
function Fail-Harness([string]$Message) {
  Write-Host "Harness 校验失败，$Message" -ForegroundColor Red
  exit 1
}

function Get-WorkflowNodeIds([string[]]$Lines) {
  @($Lines | ForEach-Object {
    if ($_ -match '^\s+- id:\s*([A-Z][A-Z0-9_]*)\s*$') { $Matches[1] }
  })
}

function Get-DefinedGateIds([string[]]$Lines) {
  @($Lines | ForEach-Object {
    if ($_ -match '^\s{2}(G[0-9]+_[A-Z0-9_]+):\s*$') { $Matches[1] }
  })
}
```

其余提取逻辑遵循同一原则：仅解析本模板稳定格式，不实现通用 YAML 解析器。

- [ ] **Step 2: 校验 state 关键字段和 phase_dir 边界**

关键字段固定为：

```powershell
$requiredStateFields = @(
  'schema_version', 'run_id', 'status', 'intent', 'risk',
  'current_node', 'next_role', 'phase_dir', 'required_nodes',
  'completed_nodes', 'blocked_by', 'artifacts', 'gates'
)
```

将 `phase_dir` 统一为 `/` 后必须匹配：

```powershell
^\.harness/phases/[^/]+$
```

随后确认解析后的绝对路径仍位于 `$Root/.harness/phases` 下且目录存在。

- [ ] **Step 3: 校验 workflow 引用**

检查：

- 路由列表和 hard rules 中引用的节点均存在。
- 每个 node 的 `role` 对应 `.harness/agents/<role>.md`。
- node gates、gate meanings 和 failure recovery 引用的门禁均在 `gates.yaml` 定义。
- failure recovery 的目标节点均存在。

- [ ] **Step 4: 校验 state 节点和已完成产物**

检查 `current_node`、`required_nodes` 和 `completed_nodes` 均为有效节点。对每个 completed node，根据 workflow 中的 `artifact` 映射检查 `$state.phase_dir/<artifact>` 存在。

- [ ] **Step 5: 运行正常模板校验**

Run:

```powershell
.\.harness\scripts\validate-harness.ps1
```

Expected: `Harness 校验通过。`，退出码为 0。

- [ ] **Step 6: 在临时副本中验证失败场景**

使用测试目录 `$env:TEMP/harness-validation-test`，复制 Harness 后分别注入未知节点、未知角色、未知门禁和越界 `phase_dir`；每个场景执行：

```powershell
.\.harness\scripts\validate-harness.ps1 -Root $testRoot
```

Expected: 每个错误场景返回非零退出码并点名具体错误；测试目录完成后仅删除该临时目录，不触碰工作区文件。

### Task 3: 同步 Shell 校验器并验证入口

**Files:**
- Modify: `.harness/scripts/validate-harness.sh`
- Verify only: `.harness/scripts/validate-harness.cmd`

- [ ] **Step 1: 用内嵌 Python 3 执行完整语义检查**

Shell 保留文件存在性检查。检测到 `python3` 时，用一个内嵌只读 Python 程序检查 JSON、phase_dir、节点、角色、门禁、恢复映射和 completed artifacts。

Python 仅使用标准库：

```python
from pathlib import Path
import json
import re
import sys
```

检测不到 Python 3 时，使用现有 `sed/grep` 完成 state 和必需门禁的基础检查，并输出“已降级为基础校验”，不得伪称执行了完整校验。

- [ ] **Step 2: 运行 Shell 校验**

Run in Git Bash、WSL 或兼容 shell：

```sh
./.harness/scripts/validate-harness.sh
```

Expected: `Harness 校验通过。`；若当前环境没有兼容 shell，在证据中记录 `BLOCKED`，不伪造结果。

- [ ] **Step 3: 运行 CMD 包装入口**

Run:

```cmd
.\.harness\scripts\validate-harness.cmd
```

Expected: 透传 PowerShell 的成功输出和退出码。

- [ ] **Step 4: 运行最终一致性检查**

Run:

```powershell
.\.harness\scripts\validate-harness.ps1
.\.harness\scripts\validate-harness.cmd
rg -n "business_code_changed_requires|TBD|TODO" .harness/workflow.yaml .harness/agents .harness/evals/runbook.md .harness/scripts/validate-harness.*
```

Expected: 两个 Windows 入口通过；旧规则名和占位符均无匹配。

### Task 4: 记录证据并完成 Harness 门禁

**Files:**
- Create: `.harness/phases/harness-light-optimization-20260719/11-development.md`
- Create: `.harness/phases/harness-light-optimization-20260719/12-compile.md`
- Create: `.harness/phases/harness-light-optimization-20260719/13-unit-test.md`
- Create: `.harness/phases/harness-light-optimization-20260719/15-evidence.json`
- Create: `.harness/phases/harness-light-optimization-20260719/18-acceptance-report.md`
- Modify: `.harness/state.json`
- Modify: `.harness/runs/harness-light-optimization-20260719/state.json`

- [ ] **Step 1: 记录开发范围和关键决策**

在 `11-development.md` 记录修改文件、解析策略、兼容性和没有新增脚本的事实。

- [ ] **Step 2: 记录静态检查和入口验证**

将 JSON 解析、PowerShell、CMD、Shell 和失败场景测试的真实命令、退出码和关键输出分别写入编译、单元测试和 evidence 产物。

- [ ] **Step 3: 按 gates.yaml 评估适用门禁**

本 run 适用 `G2_DESIGN`、`G3_COMPILE`、`G4_UNIT_TEST`、`G6_EVIDENCE` 和 `G8_ACCEPTANCE`。只能根据真实结果标记 PASS；不可用平台记录为 WAIVED 或 BLOCKED。

- [ ] **Step 4: 更新并保存 run 状态**

将完成节点、产物和门禁状态写入 `.harness/state.json`，随后执行：

```powershell
.\.harness\scripts\save-run.ps1
```

Expected: 当前 state 与 `.harness/runs/harness-light-optimization-20260719/state.json` 一致。

## 提交说明

当前仓库尚无任何 Git commit，且 Harness 文件全部未跟踪。本计划不自动创建仓库首个提交；是否建立初始提交由用户单独决定。
