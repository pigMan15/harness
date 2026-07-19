<p align="center">
  <a href="README_en.md">English</a> &nbsp;|&nbsp;
  <a href="README.md">中文</a>
</p>

# AI Coding Harness + Bridle CLI

Replace ad-hoc prompts with a file-based engineering workflow. AI-assisted development becomes **constrained, recoverable, auditable, and measurable**.

The companion **[Bridle](./harness_cli/)** CLI provides a terminal dashboard and project management.

---

## Quick Start

```bash
# Install Bridle CLI
cd harness_cli && pip install -e .

# Initialize a project
cd /path/to/your-project
bridle init

# Start a task
bridle new feat-001 --intent FEATURE --risk MEDIUM

# Check status
bridle status

# Interactive TUI dashboard
bridle
```

## Bridle Commands

| Command | Description |
|---|---|
| `bridle` | Launch TUI dashboard (multi-project, keyboard navigation) |
| `bridle init` | Initialize `.harness/` structure, append to AGENTS.md/CLAUDE.md |
| `bridle new <id> -i FEATURE -r MEDIUM` | Create a new run with auto-routed required nodes |
| `bridle status [--json]` | View progress, node list, gate summary |
| `bridle validate` | Structural integrity check (6 checks) |
| `bridle gates [--json]` | 8-gate quality panel |
| `bridle list` | List all historical runs |
| `bridle save` | Save state snapshot |
| `bridle switch <id>` | Switch active run |
| `bridle register` | Register project to global list |
| `bridle projects` | View all registered project statuses |
| `bridle --lang zh` | Switch to Chinese UI |
| `bridle knowledge init` | Initialize knowledge base skeleton |
| `bridle knowledge remote <url>` | Bind shared knowledge repository |
| `bridle knowledge extract <id>` | Extract incremental knowledge from a run |
| `bridle knowledge review <id>` | Review candidate entries (--entry N to preview one) |
| `bridle knowledge accept <id>` | Accept and write entries (--entry N for single) |
| `bridle knowledge list` | List local knowledge entries |
| `bridle knowledge search <q>` | Search the knowledge base |
| `bridle knowledge push` | Push to shared repository |
| `bridle knowledge pull` | Pull latest team knowledge |

## Knowledge Sync (Team Shared)

After each run, extract incremental engineering knowledge and sync via Git.

### First-Time Setup

```bash
# Create an empty repo on GitHub: team/shared-knowledge (uncheck all init options)

# New project (bridle init already includes knowledge skeleton):
bridle knowledge remote https://github.com/team/shared-knowledge.git
bridle knowledge push -m "init: initialize team knowledge base"

# Existing project (add skeleton):
bridle knowledge init
bridle knowledge remote https://github.com/team/shared-knowledge.git
bridle knowledge push -m "init: initialize team knowledge base"
```

### Daily Workflow

```bash
# After completing a run, promote knowledge
bridle knowledge extract feat-001       # Extract incremental knowledge
bridle knowledge review feat-001        # Review candidates
bridle knowledge review feat-001 -e 1   # Preview entry #1
bridle knowledge accept feat-001        # Accept all entries
bridle knowledge accept feat-001 -e 2   # Accept entry #2 only
bridle knowledge push                   # Push to shared repo

# bridle new auto-pulls team knowledge
bridle new feat-002 -i FEATURE -r MEDIUM
# → Output: Knowledge pulled

# Manual management
bridle knowledge pull                   # Pull latest from team
bridle knowledge list                   # List local entries
bridle knowledge search "PyInstaller"   # Search knowledge
```

## Design Principles

1. **Minimal always-on instructions** — load only the current role and needed rules
2. **State lives outside the conversation** — `state.json` is the persistent source of truth
3. **Role files split responsibilities** — 11 independent roles, each with a clear job
4. **Every phase produces auditable artifacts** — written to `phase_dir`
5. **Gates check before claiming done** — G1–G8, retry on failure

## Directory Structure

```text
.harness/
  state.json              Current persistent workflow state
  state.schema.json       State file schema
  workflow.yaml           21-node flow, intent/risk routing, G1–G8 gates
  rules/                  Atomic rules loaded on demand
  agents/                 Dispatcher, reviewer, developer, verifier, etc.
  context/                Phase-specific deep guides and templates
  phases/<run_id>/        Phase artifacts generated per run
  runs/<run_id>/          Snapshot of state.json per run
  evals/                  Gate definitions, scoring, audit checklists
  commands/               Reusable command playbooks
  knowledge/              Obsidian / LLM Wiki knowledge retention
  hooks/                  Runtime policy examples
  templates/              Reusable artifact templates
harness_cli/              Bridle CLI + TUI tool source
```

## Standard Workflow

21 nodes in total. `workflow.yaml` auto-routes based on intent and risk:

```
QUERY          → 1 node
BUG_FIX/LOW    → 6 nodes
BUG_FIX/HIGH   → 14 nodes
FEATURE/MEDIUM → 11 nodes
FEATURE/HIGH   → 20 nodes (full pipeline)
REFACTOR/MEDIUM → 9 nodes
...
```

### All 21 Nodes

| # | Node ID | Description | Role |
|---|---|---|---|
| 1 | INTAKE | Intake | dispatcher |
| 2 | CONTEXT_PACK | Context Pack | requirement-analyst |
| 3 | REQUIREMENT_REVIEW | Requirement Review | requirement-analyst |
| 4 | REQUIREMENT_CONFIRMATION | Requirement Confirmation | orchestrator |
| 5 | SOLUTION_DESIGN | Solution Design | tech-architect |
| 6 | SOLUTION_CONFIRMATION | Solution Confirmation | orchestrator |
| 7 | PRE_MORTEM | Pre-Mortem | quality-guardian |
| 8 | IMPLEMENTATION_PLAN | Implementation Plan | plan-generator |
| 9 | ACCEPTANCE_CONFIRMATION | Acceptance Confirmation | orchestrator |
| 10 | CHANGE_REQUEST | Change Request | state-keeper |
| 11 | BRANCH_CREATION | Branch Creation | state-keeper |
| 12 | WORKTREE_CREATION | Worktree Creation | state-keeper |
| 13 | CODING_DESIGN_CONFIRMATION | Coding Design Confirmation | developer |
| 14 | DEVELOPMENT | Development | developer |
| 15 | COMPILE | Compile | verifier |
| 16 | UNIT_TEST | Unit Test | verifier |
| 17 | ATDD | ATDD / Integration Test | verifier |
| 18 | EVIDENCE_CAPTURE | Evidence Capture | verifier |
| 19 | PRERELEASE_DEPLOYMENT | Prerelease Deployment | deployer |
| 20 | INTERFACE_TEST | Interface Test | tester |
| 21 | ACCEPTANCE_REPORT | Acceptance Report | orchestrator |
| 22 | KNOWLEDGE_PROMOTION | Knowledge Promotion | knowledge-keeper |

## 8 Quality Gates

| Gate | Meaning | On Failure |
|---|---|---|
| G1 | Requirements and acceptance criteria are clear | → REQUIREMENT_REVIEW |
| G2 | Design, risks, and implementation plan exist | → SOLUTION_DESIGN |
| G3 | Compile / static check passes | → DEVELOPMENT |
| G4 | Unit tests pass | → DEVELOPMENT |
| G5 | Integration / scenario validation | → DEVELOPMENT |
| G6 | Evidence file is complete | → EVIDENCE_CAPTURE |
| G7 | Prerelease deployment and interface check | → PRERELEASE_DEPLOYMENT |
| G8 | Acceptance report is complete | → ACCEPTANCE_REPORT |

Each gate auto-retries up to 2 times. Exceeding → `BLOCKED`.

## Role Model (11 roles)

`dispatcher` · `orchestrator` · `requirement-analyst` · `tech-architect` · `quality-guardian` · `plan-generator` · `developer` · `verifier` · `deployer` · `tester` · `state-keeper`

## AI-Side Usage

1. Enter from `AGENTS.md` / `CLAUDE.md`
2. Read `.harness/state.json` and `.harness/workflow.yaml`
3. Dispatcher decides next node and role based on state
4. Load only the current role file, execute node work
5. Write artifacts to `state.phase_dir`
6. Execute `gates.yaml` gates before claiming done
7. Gate failure → rollback, max 2 retries, exceeding → BLOCKED

**Iron Rule**: Source code changes = non-trivial task, MUST go through harness. No bypass excuses are valid.

## Multi-Run Management

```bash
bridle list                  # List all runs
bridle save                  # Save current snapshot
bridle switch <run-id>       # Switch to historical run
```

## Distributed Access

Bridle supports viewing all registered projects from any directory:

```bash
bridle register --path /path/to/project-a
bridle register --path /path/to/project-b
bridle projects              # View all project statuses
bridle                       # TUI dashboard, ↑↓ to switch projects
```

## Building & Releasing

```bash
cd harness_cli

# 1. Install build dependency
pip install pyinstaller

# 2. Build single-file exe
python -m PyInstaller bridle.spec --clean --noconfirm

# 3. Output (stable name for PATH)
ls -lh dist/bridle.exe            # ~15MB, no Python required

# 4. Versioned copy for GitHub Release
copy dist\bridle.exe dist\bridle-v0.1.0.exe
```

### Add to System PATH

```powershell
# Copy to a fixed directory (no version in path, permanently stable)
mkdir C:\Users\<user>\bridle
copy dist\bridle.exe C:\Users\<user>\bridle\

# Add to user PATH (Admin PowerShell)
[Environment]::SetEnvironmentVariable(
    "Path",
    $env:Path + ";C:\Users\<user>\bridle",
    [EnvironmentVariableTarget]::User
)

# Restart terminal, then available globally
bridle --version
bridle status
bridle                    # TUI dashboard
```

## Versioning

| Version Line | Location | Description |
|---|---|---|
| CLI Version | `pyproject.toml` → `version` | Semantic versioning (0.1.0) |
| Schema Version | `state.json` → `schema_version` | Bump on structural incompatibility (1.0) |
| Release Cadence | 0.x rapid iteration → 1.0 stable | MAJOR.MINOR.PATCH |

### Release Checklist

1. Update `pyproject.toml` version
2. Update `bridle.spec` output name `bridle-vX.Y.Z`
3. Run `pytest tests/` — all tests pass
4. Run `bridle validate` — structure check passes
5. Update `CHANGELOG.md`
6. Build binary: `python -m PyInstaller bridle.spec --clean --noconfirm`
7. Test binary: `dist/bridle-vX.Y.Z.exe status`
8. Git tag + push + GitHub Release

## Related Docs

- Integration Guide: `.harness/PROJECT-INTEGRATION-GUIDE.md`
- Tutorial: `.harness/TUTORIAL.md`
- Command Index: `.harness/commands/README.md`
- Bridle Source: `harness_cli/`
