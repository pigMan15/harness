"""Workflow 流程引擎：解析 workflow.yaml，提供路由决策和节点查询。

workflow.yaml 是 Harness 流程的单一事实源，定义：
- nodes: 21 个流程节点及其角色、产物、门禁
- routes: 按 intent × risk 选择最小必要路径
- hard_rules: 强制执行的节点组合
- failure_recovery: 门禁失败回退映射
- gate_meanings: 门禁含义说明
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from ..constants import WORKFLOW_FILE


# ---- 数据模型 ----


@dataclass
class Node:
    """流程节点定义。"""
    id: str
    role: str
    artifact: str | None = None
    gates: list[str] = field(default_factory=list)


@dataclass
class Workflow:
    """Harness 流程引擎。

    从 workflow.yaml 加载，提供路由决策和节点查询。
    """

    nodes: dict[str, Node]
    routes: dict[str, dict[str, list[str]]]
    hard_rules: dict[str, list[str]]
    failure_recovery: dict[str, Any]
    gate_meanings: dict[str, str]

    # ── 工厂方法 ──

    @classmethod
    def load(cls, root: str = ".") -> "Workflow":
        """从 .harness/workflow.yaml 加载并解析。

        Raises:
            FileNotFoundError: workflow.yaml 不存在
            yaml.YAMLError: YAML 格式错误
        """
        wf_path = Path(root) / WORKFLOW_FILE
        if not wf_path.exists():
            raise FileNotFoundError(f"Workflow file not found: {wf_path}")

        raw = yaml.safe_load(wf_path.read_text(encoding="utf-8"))
        if raw is None:
            raise ValueError(f"Workflow file is empty: {wf_path}")

        # 解析 nodes
        nodes: dict[str, Node] = {}
        for nd in raw.get("nodes", []):
            node = Node(
                id=nd["id"],
                role=nd.get("role", ""),
                artifact=nd.get("artifact"),
                gates=nd.get("gates", []),
            )
            nodes[node.id] = node

        # 解析其它字段
        routes: dict[str, dict[str, list[str]]] = raw.get("routes", {})
        hard_rules: dict[str, list[str]] = {}
        for rule_name, rule_nodes in raw.get("hard_rules", {}).items():
            hard_rules[rule_name] = rule_nodes

        failure_recovery: dict[str, Any] = raw.get("failure_recovery", {})
        gate_meanings: dict[str, str] = raw.get("gate_meanings", {})

        return cls(
            nodes=nodes,
            routes=routes,
            hard_rules=hard_rules,
            failure_recovery=failure_recovery,
            gate_meanings=gate_meanings,
        )

    # ── 路由 ──

    def route(self, intent: str, risk: str, enforce_hard_rules: bool = True) -> list[str]:
        """根据意图和风险返回必需节点 ID 列表。

        Args:
            intent: 意图值，如 "FEATURE", "BUG_FIX"
            risk: 风险等级，如 "LOW", "MEDIUM", "HIGH"
            enforce_hard_rules: 是否强制执行 hard_rules（默认开启）

        Returns:
            必需节点 ID 列表，按执行顺序排列。找不到匹配路由时返回空列表。
        """
        intent_routes = self.routes.get(intent, {})
        nodes = intent_routes.get(risk)
        if nodes is None:
            return []
        result = list(nodes)
        if enforce_hard_rules:
            result = self._apply_hard_rules(intent, risk, result)
        return result

    # ── hard_rules 执行 ──

    def _hard_rule_applies(self, rule_name: str, intent: str, risk: str) -> bool:
        """判断某条 hard_rule 是否适用于给定的 intent + risk。"""
        if rule_name == "code_changed_requires":
            # 所有会改代码的意图（排除 QUERY 和纯查询场景）
            return intent in ("BUG_FIX", "FEATURE", "REFACTOR")
        if rule_name == "high_risk_or_deployment_requires":
            return risk == "HIGH" or intent == "DEPLOYMENT"
        if rule_name == "high_risk_requires":
            return risk == "HIGH"
        return False

    def _apply_hard_rules(self, intent: str, risk: str, required: list[str]) -> list[str]:
        """将适用的 hard_rules 节点插入 required 列表，保持 workflow 定义顺序。

        不在 required 中已有的节点会被追加到末尾。
        """
        result = list(required)
        existing = set(result)
        all_nodes_ordered = list(self.nodes.keys())

        for rule_name, rule_nodes in self.hard_rules.items():
            if not self._hard_rule_applies(rule_name, intent, risk):
                continue
            for node_id in rule_nodes:
                if node_id not in existing:
                    result.append(node_id)
                    existing.add(node_id)

        # 按 workflow 中定义的节点顺序排序
        order_map = {nid: idx for idx, nid in enumerate(all_nodes_ordered)}
        result.sort(key=lambda nid: order_map.get(nid, 9999))
        return result

    def check_hard_rules(self, intent: str, risk: str, required: list[str]) -> list[str]:
        """检查 required 列表是否满足 hard_rules，返回缺失节点的警告消息列表。"""
        warnings: list[str] = []
        existing = set(required)
        for rule_name, rule_nodes in self.hard_rules.items():
            if not self._hard_rule_applies(rule_name, intent, risk):
                continue
            missing = [n for n in rule_nodes if n not in existing]
            if missing:
                warnings.append(
                    f"Hard rule '{rule_name}' requires missing nodes: {', '.join(missing)}"
                )
        return warnings

    def next_node(self, required: list[str], completed: set[str]) -> str | None:
        """返回第一个未完成的必需节点。

        Args:
            required: 必需节点列表
            completed: 已完成节点集合

        Returns:
            下一个节点 ID，全部完成则返回 None
        """
        for node_id in required:
            if node_id not in completed:
                return node_id
        return None

    # ── 查询 ──

    def role_for(self, node_id: str) -> str:
        """返回节点的角色。"""
        node = self.nodes.get(node_id)
        return node.role if node else ""

    def artifact_for(self, node_id: str) -> str | None:
        """返回节点的产物文件名。"""
        node = self.nodes.get(node_id)
        return node.artifact if node else None

    def gate_to_node(self, gate_id: str) -> str | None:
        """返回门禁失败时应回退到的节点 ID。"""
        g2n = self.failure_recovery.get("gate_to_node", {})
        return g2n.get(gate_id)

    def max_auto_retries(self) -> int:
        """返回每个门禁的最大自动重试次数。"""
        return self.failure_recovery.get("max_auto_retries_per_gate", 2)

    def meaning_for(self, gate_id: str) -> str:
        """返回门禁含义说明。"""
        return self.gate_meanings.get(gate_id, "")

    # ── 集合查询 ──

    def all_node_ids(self) -> set[str]:
        """返回所有节点 ID。"""
        return set(self.nodes.keys())

    def all_role_ids(self) -> set[str]:
        """返回所有角色 ID。"""
        return {n.role for n in self.nodes.values() if n.role}

    def route_nodes_referenced(self) -> set[str]:
        """返回所有路由中引用的节点 ID（用于校验）。"""
        refs: set[str] = set()
        for intent_routes in self.routes.values():
            for nodes in intent_routes.values():
                refs.update(nodes)
        return refs

    def hard_rule_nodes_referenced(self) -> set[str]:
        """返回所有硬规则中引用的节点 ID（用于校验）。"""
        refs: set[str] = set()
        for nodes in self.hard_rules.values():
            refs.update(nodes)
        return refs

    def all_gate_ids(self) -> set[str]:
        """返回 workflow 中所有的门禁 ID。"""
        gate_ids: set[str] = set()
        for node in self.nodes.values():
            gate_ids.update(node.gates)
        for gate_id in self.gate_meanings:
            gate_ids.add(gate_id)
        return gate_ids
