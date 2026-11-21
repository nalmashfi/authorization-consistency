"""Check selected manuscript aggregates against archived S7–S9 exports, without rerunning experiments."""

import csv
import json
import sys
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path


DATA_FOLDER = Path(__file__).resolve().parent


def csv_rows(path):
    with path.open(encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source))


def check(label, actual, expected):
    if actual != expected:
        raise ValueError(f"{label}: expected {expected}, found {actual}")


def check_runtime():
    folder = DATA_FOLDER / "S7_runtime"
    # Published medians are in microseconds, rounded to three decimal places.
    graphs = [
        (int(row["V"]), int(row["Lambda"]), format(Decimal(row["support_median_us"]), ".3f"),
         format(Decimal(row["complete_median_us"]), ".3f"))
        for row in csv_rows(folder / "table10_nested.csv")
    ]
    check("Table 10 graph sizes and medians", sorted(graphs), [
        (100, 96, "2.413", "6.009"), (1000, 996, "20.581", "41.853"),
        (10000, 9987, "206.411", "426.303"), (50000, 49947, "1063.372", "2133.155"),
    ])
    measurements = csv_rows(folder / "table11_runtime.csv")
    for name, expected in [("Atomic reservation", "0.240"), ("Protected commit", "0.220"),
                           ("Reservation + protected commit", "0.471")]:
        values = [format(Decimal(r["median_us"]), ".3f") for r in measurements if r["operation"] == name]
        check(f"Table 11 {name}", values, [expected])
    print("S7  Four graph sizes and three protected-operation medians match Tables 10 and 11.")


def check_coverage():
    path = DATA_FOLDER / "S8_external_validation" / "eal_preflight_report.json"
    report = json.loads(path.read_text(encoding="utf-8"))
    domains = report["domains"]
    fields = ("case_count", "authorized_trials_per_writer_condition", "selected_ordinary_trials")
    coverage = {name: tuple(row[k] for k in fields) for name, row in domains.items()}
    check("Table 14 coverage by domain", coverage, {
        "procurement": (12, 72, 8640), "cybersecurity": (16, 128, 15360), "finance": (8, 64, 7680),
    })
    for name, row in domains.items():
        enumerated = row["selected_writer_routes"] * row["ordinary_trials_per_writer_route"]
        check(f"{name} design enumeration", enumerated, row["selected_ordinary_trials"])
    total = sum(row["selected_ordinary_trials"] for row in domains.values())
    check("EAL-Bench design total", report["total_selected_ordinary_trials"], total)
    print("S8  Table 14 matches 36 cases and 31,680 selected ordinary trials in the registered design.")


def check_replay():
    folder = DATA_FOLDER / "S9_agentdojo_audit"
    cases = json.loads((folder / "agentdojo_stratified_case_index.json").read_text(encoding="utf-8"))["cases"]
    actions = csv_rows(folder / "agentdojo_stratified_action_audit.csv")
    check("Selected trajectories", len(cases), 13)
    check("Distinct case IDs", len({c["case_id"] for c in cases}), 13)
    check("Trajectories with completed actions", sum(bool(c["completed_consequential_calls"]) for c in cases), 12)
    check("Suites and model configurations", (len({c["suite"] for c in cases}), len({c["model"] for c in cases})), (3, 3))
    # Count repeated tool calls separately; several distinct calls have the same visible CSV fields.
    case_calls = Counter((c["case_id"], c["suite"], c["model"], str(c["native_utility"]),
                          str(c["native_security"]), a["tool"], str(a["supported"]))
                         for c in cases for a in c["completed_consequential_calls"])
    audit_calls = Counter((r["case_id"], r["suite"], r["model"], r["native_utility"],
                           r["native_security"], r["tool"], r["supported"]) for r in actions)
    check("Calls in case index and action audit", audit_calls, case_calls)
    decisions = Counter((r["suite"], r["supported"], r["counterfactual_gate_permitted"]) for r in actions)
    check("Table 16 archived counterfactual outcomes", decisions, {
        ("banking", "False", "False"): 13, ("travel", "False", "False"): 2, ("travel", "True", "True"): 3,
        ("workspace", "False", "False"): 2, ("workspace", "True", "True"): 1,
    })
    summary = json.loads((folder / "agentdojo_stratified_replay_results.json").read_text(encoding="utf-8"))
    totals = {
        "n_trajectories": len(cases),
        "n_trajectories_with_completed_consequential_calls": len({r["case_id"] for r in actions}),
        "n_models": len({case["model"] for case in cases}),
        "n_suites": len({case["suite"] for case in cases}),
        "completed_consequential_calls": len(actions),
        "supported_calls": sum(r["supported"] == "True" for r in actions),
        "unsupported_calls": sum(r["supported"] == "False" for r in actions),
        "trajectories_with_unsupported_effects": len({r["case_id"] for r in actions if r["supported"] == "False"}),
    }
    for name, total in totals.items():
        check(f"S9 summary {name}", summary[name], total)
    print("S9  In 13 trajectories, 21 recorded actions yield 17 unsupported denials and 4 supported permissions.")


if __name__ == "__main__":
    try:
        check_runtime()
        check_coverage()
        check_replay()
    except (OSError, KeyError, ValueError, InvalidOperation, csv.Error) as error:
        sys.exit(f"Archive check failed: {error}")
    print("Selected archive checks passed. No experiment or live benchmark was run.")
