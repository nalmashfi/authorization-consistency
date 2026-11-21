from __future__ import annotations
from typing import Any

from .base import BenchmarkAdapter, AdapterInput
from .schema import BenchmarkName, UnifiedResult


class EALBenchAdapter(BenchmarkAdapter):
    """
    Adapter for EAL-Bench.

    Expected native_record keys are intentionally minimal:
      case_id, domain, benchmark_revision
    Optional keys:
      model, model_version, provider, seed, temperature, software_revision,
      executed_at_utc, native_score, native_utility, native_attack_success,
      memory_hash, request_id, writer_architecture, writer_strategy.

    Repository-specific code should populate these fields from the immutable
    EAL-Bench run artifacts rather than altering EAL-Bench scoring.
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
            benchmark=BenchmarkName.EAL_BENCH,
            benchmark_revision=str(r.get("benchmark_revision", "unknown")),
            run_id=inp.run_id,
            repetition=inp.repetition,
            arm=inp.arm,
            case_id=str(r["case_id"]),
            domain_or_suite=str(r["domain"]),
            task_id=str(r.get("request_id")) if r.get("request_id") is not None else None,
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
            native_utility=r.get("native_utility"),
            native_attack_success=r.get("native_attack_success"),
            native_score=r.get("native_score"),
            authorization_latency_us=authorization_latency_us,
            end_to_end_latency_ms=end_to_end_latency_ms,
            native_extra={
                "memory_hash": r.get("memory_hash"),
                "writer_architecture": r.get("writer_architecture"),
                "writer_strategy": r.get("writer_strategy"),
            },
        )
