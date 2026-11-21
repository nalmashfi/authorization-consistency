from __future__ import annotations

import contextvars
import copy
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from .policy import ArmPolicy, evaluate_gate
from .schema import AuthorizationEvidence, ExperimentalArm


@dataclass(frozen=True)
class FrozenCall:
    function: str
    args: Mapping[str, Any]


@dataclass
class TaskAuthorizationContext:
    suite: str
    task_id: str
    allowed_calls: list[FrozenCall]
    arm: ExperimentalArm
    strict_unknown_tools: bool = True


_CTX: contextvars.ContextVar[TaskAuthorizationContext | None] = contextvars.ContextVar(
    "agentdojo_authorization_context", default=None
)

_TRACE: contextvars.ContextVar[list[dict[str, Any]] | None] = contextvars.ContextVar(
    "agentdojo_authorization_trace", default=None
)


def _canonical(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _canonical(value[k]) for k in sorted(value)}
    if isinstance(value, list):
        return [_canonical(v) for v in value]
    return value


def _args_match(expected: Mapping[str, Any], actual: Mapping[str, Any]) -> bool:
    """
    Exact match after removing AgentDojo placeholder-only metadata.
    This intentionally favors false rejection over false authorization.
    """
    return _canonical(dict(expected)) == _canonical(dict(actual))


def call_supported(function: str, kwargs: Mapping[str, Any], allowed: Sequence[FrozenCall]) -> bool:
    return any(
        c.function == function and _args_match(c.args, kwargs)
        for c in allowed
    )


def load_tool_policy(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _tool_classification(policy: dict[str, Any], suite: str, function: str) -> str:
    suite_policy = policy.get("suites", {}).get(suite)
    if suite_policy is None:
        return "unknown"
    if function in suite_policy.get("consequential", []):
        return "consequential"
    if function in suite_policy.get("read_only", []):
        return "read_only"
    return "unknown"


def set_task_context(ctx: TaskAuthorizationContext):
    tok1 = _CTX.set(ctx)
    tok2 = _TRACE.set([])
    return tok1, tok2


def reset_task_context(tokens):
    tok1, tok2 = tokens
    _CTX.reset(tok1)
    _TRACE.reset(tok2)


def get_trace() -> list[dict[str, Any]]:
    return list(_TRACE.get() or [])


def _append_trace(row: dict[str, Any]) -> None:
    trace = _TRACE.get()
    if trace is not None:
        trace.append(row)


def install_agentdojo_authorization_guard(
    *,
    tool_policy_path: str | Path | None = None,
    arm: ExperimentalArm | None = None,
    strict_unknown_tools: bool = True,
) -> None:
    """
    Monkey-patch AgentDojo at two narrow points:

    1. TaskSuite.run_task_with_pipeline:
       freeze legitimate consequential supports from the user task ground truth.
    2. FunctionsRuntime.run_function:
       apply the authorization gate immediately before the native function call.

    The patch leaves prompts, attacks, defenses, LLM outputs, environment objects,
    and AgentDojo utility/security scoring unchanged.
    """
    try:
        from agentdojo.base_tasks import BaseUserTask
        from agentdojo.functions_runtime import FunctionsRuntime, FunctionCall
        from agentdojo.task_suite.task_suite import TaskSuite
    except ImportError as exc:
        raise RuntimeError(
            "AgentDojo is not installed. Install the benchmark before live integration."
        ) from exc

    if getattr(FunctionsRuntime.run_function, "_authz_guard_installed", False):
        return

    default_policy_path = Path(__file__).resolve().parent / "agentdojo_tool_policy_v1.json"
    policy_path = Path(tool_policy_path) if tool_policy_path else default_policy_path
    policy = load_tool_policy(policy_path)

    selected_arm = arm or ExperimentalArm(os.getenv("AUTHZ_ARM", "B1"))

    original_run_task = TaskSuite.run_task_with_pipeline
    original_run_function = FunctionsRuntime.run_function

    def guarded_run_task(self, agent_pipeline, user_task, injection_task, injections, *args, **kwargs):
        # Build the same environment that AgentDojo will use, only to freeze a
        # deterministic authorization plan for legitimate consequential effects.
        environment = kwargs.get("environment")
        if environment is None:
            environment = self.load_and_inject_default_environment(injections)

        if isinstance(user_task, BaseUserTask):
            task_environment = user_task.init_environment(copy.deepcopy(environment))
            pre_environment = task_environment.model_copy(deep=True)
            gt = user_task.ground_truth(pre_environment)
            allowed = [
                FrozenCall(function=c.function, args=dict(c.args))
                for c in gt
                if getattr(c, "placeholder_args", None) is None
            ]
            task_id = user_task.ID
        else:
            allowed = []
            task_id = getattr(user_task, "ID", "unknown")

        ctx = TaskAuthorizationContext(
            suite=self.name,
            task_id=task_id,
            allowed_calls=allowed,
            arm=selected_arm,
            strict_unknown_tools=strict_unknown_tools,
        )
        tokens = set_task_context(ctx)
        try:
            return original_run_task(
                self, agent_pipeline, user_task, injection_task, injections, *args, **kwargs
            )
        finally:
            # Trace is intentionally left accessible only during the task.
            reset_task_context(tokens)

    def guarded_run_function(self, env, function, kwargs, raise_on_error=False):
        ctx = _CTX.get()
        if ctx is None or selected_arm in (
            ExperimentalArm.B0_NATIVE,
            ExperimentalArm.B5_NATIVE_DEFENSE,
        ):
            return original_run_function(self, env, function, kwargs, raise_on_error)

        classification = _tool_classification(policy, ctx.suite, function)

        if classification == "read_only":
            _append_trace({
                "suite": ctx.suite, "task_id": ctx.task_id, "function": function,
                "classification": classification, "gate_permitted": True,
                "reason": "read_only_tool"
            })
            return original_run_function(self, env, function, kwargs, raise_on_error)

        if classification == "unknown":
            permitted = not ctx.strict_unknown_tools
            _append_trace({
                "suite": ctx.suite, "task_id": ctx.task_id, "function": function,
                "classification": classification, "gate_permitted": permitted,
                "reason": "unknown_tool_fail_closed" if not permitted else "unknown_tool_allowed"
            })
            if not permitted:
                return "", "AuthorizationError: unknown consequentiality classification"
            return original_run_function(self, env, function, kwargs, raise_on_error)

        supported = call_supported(function, kwargs, ctx.allowed_calls)

        # AgentDojo core has no persistent authorization memory. For transfer
        # evaluation, memory validation is marked pass-by-construction/N.A.;
        # the live security question is exact current support before effect.
        evidence = AuthorizationEvidence(
            oracle_authorized=supported,
            memory_valid=True,
            support_found=supported,
            support_current=supported,
            exact_support_preserved=supported,
            reservation_acquired=supported,
            commit_revalidated=supported,
        )
        decision = evaluate_gate(ArmPolicy.for_arm(ctx.arm), evidence)

        _append_trace({
            "suite": ctx.suite,
            "task_id": ctx.task_id,
            "function": function,
            "classification": classification,
            "gate_permitted": decision.gate_permitted,
            "reason": decision.reason,
            "support_found": supported,
            "arm": ctx.arm.value,
        })

        if not decision.gate_permitted:
            return "", f"AuthorizationError: {decision.reason}"

        return original_run_function(self, env, function, kwargs, raise_on_error)

    guarded_run_function._authz_guard_installed = True  # type: ignore[attr-defined]
    FunctionsRuntime.run_function = guarded_run_function
    TaskSuite.run_task_with_pipeline = guarded_run_task


if os.getenv("AUTHZ_AGENTDOJO_ENABLE") == "1":
    install_agentdojo_authorization_guard(
        tool_policy_path=os.getenv("AUTHZ_AGENTDOJO_TOOL_POLICY"),
        arm=ExperimentalArm(os.getenv("AUTHZ_ARM", "B1")),
        strict_unknown_tools=os.getenv("AUTHZ_STRICT_UNKNOWN_TOOLS", "1") != "0",
    )
