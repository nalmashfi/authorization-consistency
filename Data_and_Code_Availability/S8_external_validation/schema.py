from __future__ import annotations

from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Any, Mapping, Optional
import json


class BenchmarkName(str, Enum):
    EAL_BENCH = "eal_bench"
    AGENTDOJO = "agentdojo"
    ASB = "asb"


class ExperimentalArm(str, Enum):
    B0_NATIVE = "B0"
    B1_FULL = "B1"
    B2_MEMORY_ONLY = "B2"
    B3_SUPPORT_ONLY = "B3"
    B4_COMMIT_ONLY = "B4"
    B5_NATIVE_DEFENSE = "B5"
    B6_NATIVE_DEFENSE_PLUS_FULL = "B6"


@dataclass(frozen=True)
class ActionProposal:
    action_id: str
    tool_name: str
    arguments: Mapping[str, Any]
    consequential: bool = True
    proposed_by_model: bool = True


@dataclass(frozen=True)
class AuthorizationEvidence:
    # Ground truth/oracle label supplied by the benchmark or a frozen mapping.
    oracle_authorized: Optional[bool] = None

    # Authorization-consistency evidence produced by the proposed model.
    memory_valid: Optional[bool] = None
    support_found: Optional[bool] = None
    support_current: Optional[bool] = None
    exact_support_preserved: Optional[bool] = None
    reservation_acquired: Optional[bool] = None
    commit_revalidated: Optional[bool] = None

    # Optional trace identifiers. Store IDs/hashes, not secrets.
    support_id: Optional[str] = None
    memory_ref_hash: Optional[str] = None
    authorization_state_hash: Optional[str] = None


@dataclass(frozen=True)
class AuthorizationDecision:
    gate_permitted: bool
    reason: str
    arm: ExperimentalArm


@dataclass
class UnifiedResult:
    schema_version: str
    benchmark: BenchmarkName
    benchmark_revision: str
    run_id: str
    repetition: int
    arm: ExperimentalArm

    # Native benchmark identity.
    case_id: str
    domain_or_suite: str
    task_id: Optional[str] = None
    attack_id: Optional[str] = None
    attack_type: Optional[str] = None
    native_defense: Optional[str] = None

    # Reproducibility metadata.
    model: Optional[str] = None
    model_version: Optional[str] = None
    provider: Optional[str] = None
    seed: Optional[int] = None
    temperature: Optional[float] = None
    software_revision: Optional[str] = None
    executed_at_utc: Optional[str] = None

    # Core paired-evaluation fields.
    oracle_authorized: Optional[bool] = None
    model_proposed_action: Optional[bool] = None
    gate_permitted: Optional[bool] = None
    external_effect_executed: Optional[bool] = None
    authorized_task_completed: Optional[bool] = None

    # Authorization trace.
    memory_revalidation_passed: Optional[bool] = None
    support_found: Optional[bool] = None
    support_current: Optional[bool] = None
    exact_support_preserved: Optional[bool] = None
    reservation_acquired: Optional[bool] = None
    commit_revalidated: Optional[bool] = None
    gate_reason: Optional[str] = None

    # Native benchmark outcomes remain separate.
    native_utility: Optional[float] = None
    native_attack_success: Optional[bool] = None
    native_score: Optional[float] = None

    # Runtime.
    authorization_latency_us: Optional[float] = None
    end_to_end_latency_ms: Optional[float] = None

    # Free-form benchmark-specific values; no claims should depend only on this field.
    native_extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["benchmark"] = self.benchmark.value
        d["arm"] = self.arm.value
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)
