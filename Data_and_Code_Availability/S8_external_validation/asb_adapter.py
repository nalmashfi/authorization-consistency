from __future__ import annotations

from .base import BenchmarkAdapter, AdapterInput
from .schema import BenchmarkName, UnifiedResult


class ASBAdapter(BenchmarkAdapter):
    """
    Adapter for Agent Security Bench (ASB).

    Expected native_record:
      scenario, case_id, benchmark_revision
    Optional:
      attack_type, attack_tool, defense_type, attack_success, refusal,
      native_score, model, model_version, provider, seed, temperature,
      software_revision.

    Only cases with a frozen deterministic authorization mapping should enter
    the primary authorization-consistency statistics.
    """

    def normalize_result(
        self,
        inp: AdapterInput,
        *,
        external_effect_executed: bool,
        authorized_task_completed: bool | None,
        authorization_latency_us: float | None = None,
        end_to_end_latency_ms: float | None = None,
    ) -> UnifiedResult:
        r = dict(inp.native_record)
        decision = self.authorize(inp)
        ev = inp.evidence

        return UnifiedResult(
            schema_version="1.0",
            benchmark=BenchmarkName.ASB,
            benchmark_revision=str(r.get("benchmark_revision", "unknown")),
            run_id=inp.run_id,
            repetition=inp.repetition,
            arm=inp.arm,
            case_id=str(r["case_id"]),
            domain_or_suite=str(r["scenario"]),
            task_id=str(r.get("task_id")) if r.get("task_id") is not None else None,
            attack_id=str(r.get("attack_tool")) if r.get("attack_tool") is not None else None,
            attack_type=r.get("attack_type"),
            native_defense=r.get("defense_type"),
            model=r.get("model"),
            model_version=r.get("model_version"),
            provider=r.get("provider"),
            seed=r.get("seed"),
            temperature=r.get("temperature"),
            software_revision=r.get("software_revision"),
            executed_at_utc=r.get("executed_at_utc"),
            oracle_authorized=ev.oracle_authorized,
            model_proposed_action=inp.proposal.proposed_by_model,
            gate_permitted=decision.gate_permitted,
            external_effect_executed=external_effect_executed,
            authorized_task_completed=authorized_task_completed,
            memory_revalidation_passed=ev.memory_valid,
            support_found=ev.support_found,
            support_current=ev.support_current,
            exact_support_preserved=ev.exact_support_preserved,
            reservation_acquired=ev.reservation_acquired,
            commit_revalidated=ev.commit_revalidated,
            gate_reason=decision.reason,
            native_attack_success=r.get("attack_success"),
            native_score=r.get("native_score"),
            authorization_latency_us=authorization_latency_us,
            end_to_end_latency_ms=end_to_end_latency_ms,
            native_extra={
                "attack_tool": r.get("attack_tool"),
                "refusal": r.get("refusal"),
            },
        )
