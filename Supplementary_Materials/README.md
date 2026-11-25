# Supplementary Materials

*A Mathematical Model for Authorization Consistency in Persistent Multiagent Artificial Intelligence Systems*  
Nabil Almashfi

For the authorization model, S1 and S2 give the proofs and the runtime checks needed to enforce its properties. For the evaluation, S3 through S9 give the experimental conditions, reported results, and limits of the available evidence. The identifiers match those in the manuscript. To locate the material supporting a particular algorithm, table, or figure, the index lists the nine supplements as follows.

| Supplement | Material | Manuscript reference |
| --- | --- | --- |
| [S1. Definitions and proofs](S1.md) | Trusted state, authorization support, protected commit, and proofs of the model properties | Formal security analysis |
| [S2. Algorithms and execution invariants](S2.md) | Pseudocode for resolving support, revalidating memory, and executing an authorized action | Algorithms 1–3 |
| [S3. Formal and controlled validation](S3.md) | Agreement with the formal oracle and decisions under four enforcement configurations | Table 6 |
| [S4. Lifecycle tests and component removal](S4.md) | Targeted lifecycle conditions and results when individual authorization checks are removed | Tables 7 and 9 |
| [S5. Stochastic validation](S5.md) | Agreement between predicted and empirical harm probabilities for the sequential and general models | Table 8 and [Figure 5](figures/Figure5_stochastic_validation_metrics.png) |
| [S6. Risk treatment](S6.md) | Additional treatment of high-risk authorized actions and friction for the remaining authorized actions | [Figure 6](figures/Figure6_AI_risk_layer_measured_results.png) |
| [S7. Runtime measurements](S7.md) | Latency by graph size and operation, with separate measurements of concurrent execution | Tables 10 and 11 and runtime analysis |
| [S8. External benchmarks](S8.md) | Registered EAL-Bench design, evidence mappings, offline checks, and scores from an independent AgentDojo evaluation | Table 12 and external validation |
| [S9. AgentDojo replay audit](S9.md) | Support labels and counterfactual gate decisions for 21 completed calls in 13 selected trajectories | Table 13 |

[Archived data, benchmark code, and verification command](../Data_and_Code_Availability/README.md)
