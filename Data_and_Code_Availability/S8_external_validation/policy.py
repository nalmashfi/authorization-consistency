from __future__ import annotations
from dataclasses import dataclass

from .schema import ExperimentalArm, AuthorizationEvidence, AuthorizationDecision


@dataclass(frozen=True)
class ArmPolicy:
    arm: ExperimentalArm
    memory_revalidation: bool
    support_resolution: bool
    exact_support_revalidation: bool
    reservation: bool
    protected_commit: bool
    native_defense: bool

    @staticmethod
    def for_arm(arm: ExperimentalArm) -> "ArmPolicy":
        if arm == ExperimentalArm.B0_NATIVE:
            return ArmPolicy(arm, False, False, False, False, False, False)
        if arm == ExperimentalArm.B1_FULL:
            return ArmPolicy(arm, True, True, True, True, True, False)
        if arm == ExperimentalArm.B2_MEMORY_ONLY:
            return ArmPolicy(arm, True, False, False, False, False, False)
        if arm == ExperimentalArm.B3_SUPPORT_ONLY:
            return ArmPolicy(arm, False, True, True, False, False, False)
        if arm == ExperimentalArm.B4_COMMIT_ONLY:
            return ArmPolicy(arm, False, False, False, False, True, False)
        if arm == ExperimentalArm.B5_NATIVE_DEFENSE:
            return ArmPolicy(arm, False, False, False, False, False, True)
        if arm == ExperimentalArm.B6_NATIVE_DEFENSE_PLUS_FULL:
            return ArmPolicy(arm, True, True, True, True, True, True)
        raise ValueError(f"Unsupported arm: {arm}")


def _require(name: str, value: bool | None) -> tuple[bool, str | None]:
    if value is None:
        return False, f"missing_{name}"
    if not value:
        return False, f"{name}_failed"
    return True, None


def evaluate_gate(policy: ArmPolicy, ev: AuthorizationEvidence) -> AuthorizationDecision:
    # B0 and B5 preserve the benchmark-native execution path. The gate is transparent.
    if policy.arm in (ExperimentalArm.B0_NATIVE, ExperimentalArm.B5_NATIVE_DEFENSE):
        return AuthorizationDecision(True, "authorization_layer_disabled", policy.arm)

    checks: list[tuple[str, bool | None]] = []

    if policy.memory_revalidation:
        checks.append(("memory_revalidation", ev.memory_valid))

    if policy.support_resolution:
        checks.extend([
            ("support_resolution", ev.support_found),
            ("support_current", ev.support_current),
        ])

    if policy.exact_support_revalidation:
        checks.append(("exact_support_revalidation", ev.exact_support_preserved))

    if policy.reservation:
        checks.append(("reservation", ev.reservation_acquired))

    if policy.protected_commit:
        checks.append(("protected_commit_revalidation", ev.commit_revalidated))

    for name, value in checks:
        ok, reason = _require(name, value)
        if not ok:
            return AuthorizationDecision(False, reason or "authorization_denied", policy.arm)

    return AuthorizationDecision(True, "authorization_consistency_checks_passed", policy.arm)
