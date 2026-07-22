"""pytest fixtures: 创建临时 .harness/ 目录用于测试。"""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def temp_project() -> Path:
    """创建临时项目目录，复制 .harness/ 模板用于测试。"""
    tmp = Path(tempfile.mkdtemp(prefix="bridle-test-"))
    yield tmp
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def valid_harness(temp_project: Path) -> Path:
    """在临时目录中创建完整合法的 .harness/ 结构。"""
    harness_dir = temp_project / ".harness"
    # 复制模板
    templates = Path(__file__).resolve().parent.parent / "src/harness_cli/templates/.harness"
    if templates.exists():
        shutil.copytree(templates, harness_dir)
    else:
        harness_dir.mkdir(parents=True)

    # 确保核心文件存在
    (harness_dir / "state.schema.json").write_text(_STATE_SCHEMA, encoding="utf-8")
    (harness_dir / "workflow.yaml").write_text(_MINIMAL_WORKFLOW, encoding="utf-8")
    (harness_dir / "evals/gates.yaml").parent.mkdir(parents=True, exist_ok=True)
    (harness_dir / "evals/gates.yaml").write_text(_MINIMAL_GATES, encoding="utf-8")

    # 写一个干净的 state.json
    state = {
        "schema_version": "1.0",
        "run_id": "test-run-001",
        "status": "ROUTING",
        "intent": "FEATURE",
        "risk": "MEDIUM",
        "current_node": "INTAKE",
        "next_role": "dispatcher",
        "phase_dir": ".harness/phases/test-run-001",
        "required_nodes": ["INTAKE", "DEVELOPMENT", "COMPILE", "EVIDENCE_CAPTURE", "ACCEPTANCE_REPORT"],
        "completed_nodes": [],
        "blocked_by": [],
        "artifacts": {},
        "gates": {
            "G1_REQUIREMENTS": "NOT_RUN",
            "G2_DESIGN": "NOT_RUN",
            "G3_COMPILE": "NOT_RUN",
            "G4_UNIT_TEST": "NOT_RUN",
            "G5_ATDD": "NOT_RUN",
            "G6_EVIDENCE": "NOT_RUN",
            "G7_PRERELEASE": "NOT_RUN",
            "G8_ACCEPTANCE": "NOT_RUN",
        },
        "retry_counts": {},
        "last_updated": "2026-07-19T00:00:00+00:00",
        "notes": "Test run",
    }
    (harness_dir / "state.json").write_text(
        json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # 确保必需目录
    (harness_dir / "phases/test-run-001").mkdir(parents=True, exist_ok=True)
    (harness_dir / "runs").mkdir(parents=True, exist_ok=True)
    (harness_dir / "phases").mkdir(parents=True, exist_ok=True)
    for d in ["agents", "rules"]:
        (harness_dir / d).mkdir(parents=True, exist_ok=True)
    for agent in ["dispatcher", "developer", "verifier"]:
        (harness_dir / f"agents/{agent}.md").touch()
    for rule in ["artifact-location", "build", "safety", "evidence"]:
        (harness_dir / f"rules/{rule}.md").touch()

    # .gitkeep
    (harness_dir / "runs/.gitkeep").touch()
    (harness_dir / "phases/.gitkeep").touch()

    # AGENTS.md
    (temp_project / "AGENTS.md").write_text("Test AGENTS.md\n")

    return temp_project


def _ensure_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")


_STATE_SCHEMA = json.dumps({
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Harness State",
    "type": "object",
    "required": ["schema_version", "run_id", "status", "intent", "risk", "current_node", "next_role", "phase_dir", "required_nodes", "completed_nodes", "blocked_by", "artifacts", "gates"],
    "properties": {
        "schema_version": {"type": "string"},
        "run_id": {"type": "string"},
        "status": {"type": "string"},
        "intent": {"type": "string"},
        "risk": {"type": "string"},
        "current_node": {"type": "string"},
        "next_role": {"type": "string"},
        "phase_dir": {"type": "string"},
        "required_nodes": {"type": "array", "items": {"type": "string"}},
        "completed_nodes": {"type": "array", "items": {"type": "string"}},
        "blocked_by": {"type": "array", "items": {"type": "string"}},
        "artifacts": {"type": "object"},
        "gates": {"type": "object"},
        "retry_counts": {"type": "object"},
        "last_updated": {"type": ["string", "null"]},
        "notes": {"type": "string"},
    },
})

_MINIMAL_WORKFLOW = """
schema_version: "1.0"
artifact_root: "state.phase_dir"

nodes:
  - id: INTAKE
    role: dispatcher
    artifact: "00-intake.md"
  - id: DEVELOPMENT
    role: developer
    artifact: "11-development.md"
  - id: COMPILE
    role: verifier
    artifact: "12-compile.md"
    gates: ["G3_COMPILE"]
  - id: EVIDENCE_CAPTURE
    role: verifier
    artifact: "15-evidence.json"
    gates: ["G6_EVIDENCE"]
  - id: ACCEPTANCE_REPORT
    role: orchestrator
    artifact: "18-acceptance-report.md"
    gates: ["G8_ACCEPTANCE"]

routes:
  FEATURE:
    LOW: ["INTAKE", "DEVELOPMENT", "COMPILE", "EVIDENCE_CAPTURE", "ACCEPTANCE_REPORT"]
    MEDIUM: ["INTAKE", "DEVELOPMENT", "COMPILE", "EVIDENCE_CAPTURE", "ACCEPTANCE_REPORT"]
  BUG_FIX:
    LOW: ["INTAKE", "DEVELOPMENT", "COMPILE", "EVIDENCE_CAPTURE", "ACCEPTANCE_REPORT"]
  REFACTOR:
    LOW: ["INTAKE", "DEVELOPMENT", "COMPILE", "EVIDENCE_CAPTURE", "ACCEPTANCE_REPORT"]

hard_rules:
  code_changed_requires:
    - COMPILE
    - EVIDENCE_CAPTURE

failure_recovery:
  max_auto_retries_per_gate: 2
  gate_to_node:
    G3_COMPILE: DEVELOPMENT
    G6_EVIDENCE: EVIDENCE_CAPTURE
    G8_ACCEPTANCE: ACCEPTANCE_REPORT

gate_meanings:
  G3_COMPILE: "must compile"
  G6_EVIDENCE: "must have evidence"
  G8_ACCEPTANCE: "must have report"
"""

_MINIMAL_GATES = """
schema_version: "1.0"
gates:
  G1_REQUIREMENTS:
    description: "requirements are clear"
  G2_DESIGN:
    description: "design exists"
  G3_COMPILE:
    description: "code compiles"
    required_artifacts:
      - "12-compile.md"
  G4_UNIT_TEST:
    description: "unit tests pass"
  G5_ATDD:
    description: "scenario tests pass"
  G6_EVIDENCE:
    description: "evidence recorded"
    required_artifacts:
      - "15-evidence.json"
  G7_PRERELEASE:
    description: "prerelease checks pass"
  G8_ACCEPTANCE:
    description: "report exists"
    required_artifacts:
      - "18-acceptance-report.md"
"""
