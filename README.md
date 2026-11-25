# A Mathematical Model for Authorization Consistency in Persistent Multiagent Artificial Intelligence Systems

**Nabil Almashfi**  
Department of Software Engineering, College of Computer and Information Sciences, Jouf University

In a persistent multiagent system, an agent can retrieve a delegation record after the grant it describes has expired or been revoked. At protected commit, the proposed model checks whether the exact support bound to the execution remains valid under current trusted state. Nine supplements accompany the study. For the formal analysis, experimental results, and archived records, the two directories provide the materials listed below.

| Directory | Contents |
| --- | --- |
| [Supplementary Materials](Supplementary_Materials/README.md) | S1–S9, including definitions and proofs, algorithm pseudocode, experimental results, and the scope of each benchmark comparison. |
| [Data and Code Availability](Data_and_Code_Availability/README.md) | Runtime summaries, benchmark mappings, and an audit of recorded AgentDojo calls. The directory guide identifies the available inputs and gives instructions for checking Tables 10–13. |

## Verify the archived results

From the repository root, run the following command with Python 3.

```sh
python3 Data_and_Code_Availability/verify_reported_results.py
```

The script checks reported values against the archived records. The core algorithms are available as [pseudocode in S2](Supplementary_Materials/S2.md).
