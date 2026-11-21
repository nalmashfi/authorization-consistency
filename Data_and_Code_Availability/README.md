# Data and Code Availability

*A Mathematical Model for Authorization Consistency in Persistent Multiagent Artificial Intelligence Systems*

For the evaluation of authorization consistency, this repository provides runtime measurements, external benchmark records, and an audit of completed calls in selected AgentDojo trajectories. Alongside the formal model, the [supplements](../Supplementary_Materials/README.md) give the results of the internal experiments used to assess authorization consistency. The core algorithms appear in pseudocode. The executable core implementation and the original experiment scripts are unavailable here. To identify the records behind each part of the evaluation, the table describes the contents of the three directories as follows.

| Records | Available data and code | Scope |
| --- | --- | --- |
| [S7 runtime](S7_runtime/) | Timing summaries, fitted values, and measurements by concurrency level | Each timing summary describes a configuration. The individual timing observations are unavailable. |
| [S8 external benchmarks](S8_external_validation/) | Registered design, benchmark mapping code, authorization policy, offline checks, and independent AgentDojo scores | The counts establish the size of the registered design. The repository omits the raw EAL-Bench trials and frozen memories. |
| [S9 AgentDojo audit](S9_agentdojo_audit/) | Case index, authorization decisions for individual completed calls, and replay summaries | The decision counts can be checked against the recorded support labels. To reassess a label, a reader needs the original task and the arguments of the call. |

For the internal experiments, S3 through S6 report the results of formal validation, controlled comparisons, lifecycle tests, stochastic validation, and risk treatment. The repository omits the individual case logs, the trace vectors for each setting, the risk predictions for each case, and the exact classifier hyperparameters. In S8, the EAL-Bench and Agent Security Bench adapters require a base module absent from the source release. Each benchmark project sets the terms for access to its materials.

## Check the reported values

To verify selected manuscript results, the [verification script](verify_reported_results.py) reads the archived records offline using the Python 3 standard library. First, the script compares the median latencies in the S7 timing files with the values reported in Tables 10 and 11. Next, it checks the counts in Table 14 against the registered S8 design. Finally, it compares the S9 case index with the action audit, then checks the counterfactual decisions against Table 16. From the repository root, the command is as follows.

```sh
python3 Data_and_Code_Availability/verify_reported_results.py
```
