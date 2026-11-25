# Data and Code Availability

*A Mathematical Model for Authorization Consistency in Persistent Multiagent Artificial Intelligence Systems*  
Nabil Almashfi

For the runtime evaluation, S7 provides measurements by graph size, operation, and concurrency level in the configurations reported in the manuscript. For the external benchmarks, S8 documents the registered design and the evidence mappings, while S9 records decisions on individual AgentDojo calls. The replay uses previously recorded calls. To locate the source of a manuscript value, the correspondence between results and files is as follows.

| Manuscript result | Archived files | Evidence supplied |
| --- | --- | --- |
| Table 10 | [Nested timing measurements](S7_runtime/table10_nested.csv) | Summary of paired support-resolution and complete-path timings by graph size |
| Table 11 and concurrent execution | [Operation timings](S7_runtime/table11_runtime.csv), [concurrent timings](S7_runtime/concurrency_runtime.csv), [runtime summary](S7_runtime/runtime_v3_summary.json) | Latencies by operation, throughput by concurrency level, measurement environment, and memory fit |
| Table 12 | [EAL-Bench design](S8_external_validation/eal_public_design_snapshot.json), [offline coverage counts](S8_external_validation/eal_preflight_report.json) | Registered trial counts by domain. Computing a protected-path execution rate would require case-level evidence of effects. |
| External benchmark mappings | [S8 file index](../Supplementary_Materials/S8.md#s86-supplied-machine-readable-files), [mapping code and policy](S8_external_validation/) | Evidence schema, tool policy, adapters, and offline checks for the external benchmarks |
| Independent AgentDojo evaluation | [Suite-level scores](S8_external_validation/independent_agentdojo_full_benchmark_context.csv), [combined scores](S8_external_validation/independent_agentdojo_context.json) | Native utility and security scores from a separate evaluation whose agents ran without the proposed authorization gate |
| Table 13 | [Trajectory index](S9_agentdojo_audit/agentdojo_stratified_case_index.json), [action audit](S9_agentdojo_audit/agentdojo_stratified_action_audit.csv), [replay summary](S9_agentdojo_audit/agentdojo_stratified_replay_results.json) | Support labels and counterfactual gate decisions for 21 completed calls in 13 selected trajectories. The index omits the original call arguments. |

## Verify the archived results

The verification script uses only the Python 3 standard library. For Tables 10 and 11, the script checks the graph sizes and median latencies in every row against the archived timing files. For Table 12, it checks the EAL-Bench counts for each domain against the registered design and verifies the combined trial count. For Table 13, it matches the trajectory index to the action audit and checks the replay totals against the archived summary. From the repository root, the command to run the offline checks against these archived files is as follows.

```sh
python3 Data_and_Code_Availability/verify_reported_results.py
```

## Scope of reproduction

For the internal experiments, the release provides the reported summaries but omits individual formal, controlled, and lifecycle case logs, per-setting stochastic trace vectors, case-level risk predictions, and individual timing observations. The core algorithms appear as [pseudocode in S2](../Supplementary_Materials/S2.md). For a new experimental run, the executable core implementation, original experiment and timing scripts, and exact Gradient Boosting hyperparameters are unavailable in this release. In S8, the EAL-Bench and Agent Security Bench adapters both import a base module that the release does not supply. For EAL-Bench, the original trial records and the frozen memories used to generate proposals are unavailable in the archive. Access to external benchmark data is subject to the distribution terms of the corresponding project.
