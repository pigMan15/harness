"""Structured validation for a Bridle harness project."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import jsonschema

from ..constants import (
    REQUIRED_FILES,
    STATE_FILE,
    SCHEMA_FILE,
    WORKFLOW_FILE,
    GATES_FILE,
    PHASES_DIR,
)
from .workflow import Workflow
from .gates import GateEvaluator


@dataclass
class ValidationIssue:
    """A single validation issue."""

    level: str  # "error" | "warning"
    message: str
    file: str | None = None
    detail: str | None = None


@dataclass
class ValidationReport:
    """Aggregated validation report."""

    passed: bool
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)

    @property
    def issue_count(self) -> int:
        return len(self.errors) + len(self.warnings)

    def format_summary(self) -> str:
        parts = []
        if self.errors:
            parts.append(f"{len(self.errors)} error(s)")
        if self.warnings:
            parts.append(f"{len(self.warnings)} warning(s)")
        if not parts:
            return "No issues found"
        return ", ".join(parts)


class Validator:
    """Validate .harness structure, references, paths, and active state."""

    def __init__(self, root: str = ".", strict: bool = False):
        self.root = Path(root).resolve()
        self.strict = strict

    def validate(self) -> ValidationReport:
        errors: list[ValidationIssue] = []
        warnings: list[ValidationIssue] = []

        errors.extend(self._check_required_files())
        errors.extend(self._check_state_json())
        errors.extend(self._check_workflow())
        errors.extend(self._check_phase_dir_safety())
        errors.extend(self._check_gate_definitions())
        warnings.extend(self._check_artifacts())

        if self.strict:
            errors.extend(warnings)
            warnings = []

        return ValidationReport(passed=len(errors) == 0, errors=errors, warnings=warnings)

    def _check_required_files(self) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for rel_path in REQUIRED_FILES:
            full_path = self.root / rel_path
            if not full_path.exists():
                issues.append(ValidationIssue(
                    level="error",
                    message=f"Missing required file: {rel_path}",
                    file=rel_path,
                ))
        return issues

    def _check_state_json(self) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        state_path = self.root / STATE_FILE

        if not state_path.exists():
            issues.append(ValidationIssue(
                level="error",
                message="state.json not found - cannot perform schema validation",
                file=STATE_FILE,
            ))
            return issues

        try:
            raw = json.loads(state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            issues.append(ValidationIssue(
                level="error",
                message=f"state.json is not valid JSON: {e.msg}",
                file=STATE_FILE,
            ))
            return issues

        schema_path = self.root / SCHEMA_FILE
        if schema_path.exists():
            try:
                schema = json.loads(schema_path.read_text(encoding="utf-8"))
                jsonschema.validate(raw, schema)
            except jsonschema.ValidationError as e:
                issues.append(ValidationIssue(
                    level="error",
                    message=f"state.json schema validation failed: {e.message}",
                    file=STATE_FILE,
                ))

        phase_dir = raw.get("phase_dir", "")
        normalized = str(phase_dir).replace("\\", "/")
        if not normalized.startswith(".harness/phases/"):
            issues.append(ValidationIssue(
                level="error",
                message=f"phase_dir must be under .harness/phases/: {phase_dir}",
                file=STATE_FILE,
            ))

        issues.extend(self._check_required_nodes_route(raw))
        return issues

    def _check_required_nodes_route(self, raw_state: dict) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        wf_path = self.root / WORKFLOW_FILE
        if not wf_path.exists():
            return issues

        try:
            workflow = Workflow.load(str(self.root))
        except Exception as e:
            return [ValidationIssue(
                level="error",
                message=f"state/workflow route validation failed: {e}",
                file=STATE_FILE,
            )]

        intent = str(raw_state.get("intent", ""))
        risk = str(raw_state.get("risk", ""))
        expected_nodes = workflow.route(intent, risk)
        actual_nodes = list(raw_state.get("required_nodes", []))

        # Active state must stay aligned with the current workflow route.
        if expected_nodes and actual_nodes != expected_nodes:
            issues.append(ValidationIssue(
                level="error",
                message="state.required_nodes does not match workflow route",
                file=STATE_FILE,
                detail=f"intent={intent} risk={risk} expected={expected_nodes} actual={actual_nodes}",
            ))
        elif not expected_nodes:
            issues.append(ValidationIssue(
                level="error",
                message=f"No workflow route for {intent}/{risk}",
                file=WORKFLOW_FILE,
            ))
        return issues

    def _check_workflow(self) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        wf_path = self.root / WORKFLOW_FILE

        if not wf_path.exists():
            issues.append(ValidationIssue(
                level="error",
                message="workflow.yaml not found",
                file=WORKFLOW_FILE,
            ))
            return issues

        try:
            workflow = Workflow.load(str(self.root))
        except Exception as e:
            issues.append(ValidationIssue(
                level="error",
                message=f"workflow.yaml parse error: {e}",
                file=WORKFLOW_FILE,
            ))
            return issues

        node_ids = workflow.all_node_ids()

        for node_id, node in workflow.nodes.items():
            if node.role:
                role_path = self.root / f".harness/agents/{node.role}.md"
                if not role_path.exists():
                    issues.append(ValidationIssue(
                        level="error",
                        message=f"Node '{node_id}' references missing role: {node.role}",
                        file=WORKFLOW_FILE,
                        detail=f"Expected file: .harness/agents/{node.role}.md",
                    ))

        for node_id in workflow.route_nodes_referenced():
            if node_id not in node_ids:
                issues.append(ValidationIssue(
                    level="error",
                    message=f"Route references unknown node: {node_id}",
                    file=WORKFLOW_FILE,
                ))

        for node_id in workflow.hard_rule_nodes_referenced():
            if node_id not in node_ids:
                issues.append(ValidationIssue(
                    level="error",
                    message=f"Hard rule references unknown node: {node_id}",
                    file=WORKFLOW_FILE,
                ))

        gate_to_node = workflow.failure_recovery.get("gate_to_node", {})
        for gate_id, node_id in gate_to_node.items():
            if node_id not in node_ids:
                issues.append(ValidationIssue(
                    level="error",
                    message=f"failure_recovery references unknown node: {node_id} (gate: {gate_id})",
                    file=WORKFLOW_FILE,
                ))

        return issues

    def _check_phase_dir_safety(self) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        state_path = self.root / STATE_FILE

        if not state_path.exists():
            return issues

        try:
            raw = json.loads(state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return issues

        phase_dir = str(raw.get("phase_dir", ""))
        phase_path = (self.root / phase_dir).resolve()
        phases_root = (self.root / PHASES_DIR).resolve()

        try:
            phase_path.relative_to(phases_root)
        except ValueError:
            issues.append(ValidationIssue(
                level="error",
                message=f"phase_dir is outside .harness/phases/: {phase_dir}",
                file=STATE_FILE,
                detail=f"Resolved to: {phase_path}, expected under: {phases_root}",
            ))

        return issues

    def _check_gate_definitions(self) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        gates_path = self.root / GATES_FILE
        state_path = self.root / STATE_FILE

        if not gates_path.exists():
            issues.append(ValidationIssue(
                level="error",
                message="gates.yaml not found",
                file=GATES_FILE,
            ))
            return issues

        if not state_path.exists():
            return issues

        try:
            evaluator = GateEvaluator.load(str(self.root))
            raw_state = json.loads(state_path.read_text(encoding="utf-8"))
        except Exception as e:
            issues.append(ValidationIssue(
                level="error",
                message=f"Gate validation error: {e}",
                file=GATES_FILE,
            ))
            return issues

        defined_gates = evaluator.all_gate_ids()
        state_gates = set(raw_state.get("gates", {}).keys())

        for gate_id in state_gates:
            if gate_id not in defined_gates:
                issues.append(ValidationIssue(
                    level="error",
                    message=f"state.json references unknown gate: {gate_id}",
                    file=STATE_FILE,
                ))

        return issues

    def _check_artifacts(self) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        state_path = self.root / STATE_FILE
        wf_path = self.root / WORKFLOW_FILE

        if not state_path.exists() or not wf_path.exists():
            return issues

        try:
            raw = json.loads(state_path.read_text(encoding="utf-8"))
            workflow = Workflow.load(str(self.root))
        except Exception:
            return issues

        phase_dir = str(raw.get("phase_dir", ""))
        phase_path = self.root / phase_dir
        completed = set(raw.get("completed_nodes", []))

        for node_id in completed:
            artifact = workflow.artifact_for(node_id)
            if artifact and not (phase_path / artifact).exists():
                issues.append(ValidationIssue(
                    level="warning",
                    message=f"Completed node '{node_id}' is missing artifact: {artifact}",
                    file=f"{phase_dir}/{artifact}",
                ))

        return issues
