"""HarnessState 状态管理：state.json 的读写、校验和操作。

所有对 state.json 的修改都必须经过本模块，确保 schema 校验始终生效。
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

import jsonschema

from ..constants import SCHEMA_FILE, HARNESS_DIR, PHASES_DIR, RUNS_DIR, STATE_FILE


class RunStatus(str, Enum):
    """Run 生命周期状态。"""
    IDLE = "IDLE"
    ROUTING = "ROUTING"
    IN_PROGRESS = "IN_PROGRESS"
    REVIEWING = "REVIEWING"
    DESIGNING = "DESIGNING"
    PLANNING = "PLANNING"
    DEVELOPING = "DEVELOPING"
    VERIFYING = "VERIFYING"
    DEPLOYING = "DEPLOYING"
    TESTING = "TESTING"
    REPORTING = "REPORTING"
    BLOCKED = "BLOCKED"
    DONE = "DONE"
    COMPLETED = "COMPLETED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"


class Intent(str, Enum):
    """任务意图分类。"""
    UNKNOWN = "UNKNOWN"
    QUERY = "QUERY"
    BUG_FIX = "BUG_FIX"
    FEATURE = "FEATURE"
    REFACTOR = "REFACTOR"
    DEPLOYMENT = "DEPLOYMENT"
    INCIDENT = "INCIDENT"


class Risk(str, Enum):
    """任务风险等级。"""
    UNKNOWN = "UNKNOWN"
    NA = "NA"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


# ---- JSON Schema 缓存 ----


def _load_schema(root: str = ".") -> dict:
    """加载 state.schema.json，缓存于模块级别。"""
    schema_path = Path(root) / SCHEMA_FILE
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    return json.loads(schema_path.read_text(encoding="utf-8"))


# ---- 数据模型 ----


@dataclass
class HarnessState:
    """Harness 流程状态的完整内存模型。

    与 .harness/state.json 一一对应，加载时校验 schema，保存时写回 JSON。
    """

    schema_version: str
    run_id: str
    status: RunStatus
    intent: Intent
    risk: Risk
    current_node: str
    next_role: str
    phase_dir: str
    required_nodes: list[str] = field(default_factory=list)
    completed_nodes: list[str] = field(default_factory=list)
    blocked_by: list[str] = field(default_factory=list)
    artifacts: dict[str, str] = field(default_factory=dict)
    gates: dict[str, str] = field(default_factory=dict)
    retry_counts: dict[str, int] = field(default_factory=dict)
    last_updated: str | None = None
    notes: str = ""

    # ── 工厂方法 ──

    @classmethod
    def load(cls, root: str = ".") -> "HarnessState":
        """从 .harness/state.json 加载，校验 schema，返回 HarnessState 实例。

        Raises:
            FileNotFoundError: state.json 不存在
            jsonschema.ValidationError: JSON 不符合 schema
        """
        state_path = Path(root) / STATE_FILE
        if not state_path.exists():
            raise FileNotFoundError(f"State file not found: {state_path}")

        raw = json.loads(state_path.read_text(encoding="utf-8"))
        schema = _load_schema(root)
        jsonschema.validate(raw, schema)

        return cls(
            schema_version=raw["schema_version"],
            run_id=raw["run_id"],
            status=RunStatus(raw["status"]),
            intent=Intent(raw["intent"]),
            risk=Risk(raw["risk"]),
            current_node=raw["current_node"],
            next_role=raw.get("next_role") or "",
            phase_dir=raw["phase_dir"],
            required_nodes=raw.get("required_nodes", []),
            completed_nodes=raw.get("completed_nodes", []),
            blocked_by=raw.get("blocked_by", []),
            artifacts=raw.get("artifacts", {}),
            gates=raw.get("gates", {}),
            retry_counts=raw.get("retry_counts", {}),
            last_updated=raw.get("last_updated"),
            notes=raw.get("notes", ""),
        )

    @classmethod
    def create_new(
        cls,
        run_id: str,
        intent: Intent,
        risk: Risk,
        root: str = ".",
    ) -> "HarnessState":
        """创建一个全新的 HarnessState 实例（不写入磁盘）。"""
        phase_dir = f".harness/phases/{run_id}"
        return cls(
            schema_version="1.0",
            run_id=run_id,
            status=RunStatus.ROUTING,
            intent=intent,
            risk=risk,
            current_node="INTAKE",
            next_role="dispatcher",
            phase_dir=phase_dir,
            required_nodes=[],
            completed_nodes=[],
            blocked_by=[],
            artifacts={},
            gates={
                "G1_REQUIREMENTS": "NOT_RUN",
                "G2_DESIGN": "NOT_RUN",
                "G3_COMPILE": "NOT_RUN",
                "G4_UNIT_TEST": "NOT_RUN",
                "G5_ATDD": "NOT_RUN",
                "G6_EVIDENCE": "NOT_RUN",
                "G7_PRERELEASE": "NOT_RUN",
                "G8_ACCEPTANCE": "NOT_RUN",
            },
            retry_counts={},
            last_updated=datetime.now(timezone.utc).isoformat(),
            notes=f"Run initialized by bridle. Intent={intent.value}, Risk={risk.value}.",
        )

    # ── 序列化 ──

    def to_dict(self) -> dict[str, Any]:
        """转为可 JSON 序列化的 dict。"""
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "status": self.status.value,
            "intent": self.intent.value,
            "risk": self.risk.value,
            "current_node": self.current_node,
            "next_role": self.next_role,
            "phase_dir": self.phase_dir,
            "required_nodes": self.required_nodes,
            "completed_nodes": self.completed_nodes,
            "blocked_by": self.blocked_by,
            "artifacts": self.artifacts,
            "gates": self.gates,
            "retry_counts": self.retry_counts,
            "last_updated": self.last_updated,
            "notes": self.notes,
        }

    def save(self, root: str = ".") -> None:
        """写回 .harness/state.json。"""
        self.last_updated = datetime.now(timezone.utc).isoformat()
        state_path = Path(root) / STATE_FILE
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def save_snapshot(self, root: str = ".") -> Path:
        """保存到 .harness/runs/<run_id>/state.json，返回快照路径。"""
        self.last_updated = datetime.now(timezone.utc).isoformat()
        snapshot_dir = Path(root) / RUNS_DIR / self.run_id
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        snapshot_path = snapshot_dir / "state.json"
        snapshot_path.write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return snapshot_path

    # ── 查询方法 ──

    def progress(self) -> tuple[int, int]:
        """返回 (已完成, 总必需) 节点数。"""
        completed = len(self.completed_nodes)
        total = len(self.required_nodes)
        return completed, total

    def progress_pct(self) -> float:
        """返回进度百分比 0.0 ~ 1.0。"""
        _, total = self.progress()
        if total == 0:
            return 0.0
        completed, _ = self.progress()
        return completed / total

    def is_gate_pass(self, gate_id: str) -> bool:
        """检查单个门禁是否已通过。"""
        return self.gates.get(gate_id, "NOT_RUN") == "PASS"

    def all_gates_pass(self) -> bool:
        """全部门禁均已通过或标记为不要求。"""
        for status in self.gates.values():
            if status not in ("PASS", "NOT_REQUIRED", "WAIVED"):
                return False
        return True

    def next_required_node(self) -> str | None:
        """返回第一个未完成的必需节点。"""
        completed_set = set(self.completed_nodes)
        for node in self.required_nodes:
            if node not in completed_set:
                return node
        return None


# ---- Run 管理函数 ----


def list_runs(root: str = ".") -> list[dict[str, Any]]:
    """扫描 .harness/runs/ 目录，返回所有 run 的摘要列表。

    每个摘要包含: run_id, status, intent, risk, current_node, progress, last_updated
    """
    runs_path = Path(root) / RUNS_DIR
    if not runs_path.exists():
        return []

    result = []
    for run_dir in sorted(runs_path.iterdir(), reverse=True):
        if not run_dir.is_dir():
            continue
        state_file = run_dir / "state.json"
        if not state_file.exists():
            continue

        try:
            raw = json.loads(state_file.read_text(encoding="utf-8"))
            result.append({
                "run_id": raw.get("run_id", run_dir.name),
                "status": raw.get("status", "UNKNOWN"),
                "intent": raw.get("intent", "UNKNOWN"),
                "risk": raw.get("risk", "UNKNOWN"),
                "current_node": raw.get("current_node", ""),
                "completed": len(raw.get("completed_nodes", [])),
                "required": len(raw.get("required_nodes", [])),
                "last_updated": raw.get("last_updated", ""),
            })
        except (json.JSONDecodeError, KeyError):
            result.append({
                "run_id": run_dir.name,
                "status": "CORRUPTED",
                "intent": "UNKNOWN",
                "risk": "UNKNOWN",
                "current_node": "",
                "completed": 0,
                "required": 0,
                "last_updated": "",
            })

    return result


def switch_run(run_id: str, root: str = ".") -> HarnessState:
    """从 .harness/runs/<run_id>/state.json 恢复指定 run，写回 state.json。

    Raises:
        FileNotFoundError: 目标 run 的快照不存在
    """
    snapshot_path = Path(root) / RUNS_DIR / run_id / "state.json"
    if not snapshot_path.exists():
        raise FileNotFoundError(f"Run snapshot not found: {snapshot_path}")

    # 先加载快照中的状态（用快照所在目录的 schema）
    raw = json.loads(snapshot_path.read_text(encoding="utf-8"))
    schema = _load_schema(root)
    jsonschema.validate(raw, schema)

    state = HarnessState(
        schema_version=raw["schema_version"],
        run_id=raw["run_id"],
        status=RunStatus(raw["status"]),
        intent=Intent(raw["intent"]),
        risk=Risk(raw["risk"]),
        current_node=raw["current_node"],
        next_role=raw.get("next_role") or "",
        phase_dir=raw["phase_dir"],
        required_nodes=raw.get("required_nodes", []),
        completed_nodes=raw.get("completed_nodes", []),
        blocked_by=raw.get("blocked_by", []),
        artifacts=raw.get("artifacts", {}),
        gates=raw.get("gates", {}),
        retry_counts=raw.get("retry_counts", {}),
        last_updated=datetime.now(timezone.utc).isoformat(),
        notes=f"Switched from snapshot: {run_id}",
    )

    # 写回 state.json
    state.save(root)
    return state


def ensure_phase_dir(state: HarnessState, root: str = ".") -> Path:
    """确保 phase_dir 目录存在，创建它如果不存在。返回绝对路径。"""
    phase_path = Path(root) / state.phase_dir
    phase_path.mkdir(parents=True, exist_ok=True)
    return phase_path
