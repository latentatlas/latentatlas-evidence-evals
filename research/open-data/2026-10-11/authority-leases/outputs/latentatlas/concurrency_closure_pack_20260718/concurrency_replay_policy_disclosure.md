# Replay Policy Disclosure

The local replay is not presented as an independent policy-engine result.
It is an automatic diagnostic replay that reads frozen review judgments and maps them into block versus hold/revalidate lanes.

| Question | Answer |
| --- | --- |
| Replay independent of review labels? | No. It is a label-conditioned diagnostic replay. |
| Policy defined before labels? | False |
| Policy code reads review judgments? | True |
| Thresholds tuned after results? | False |
| Execution mode | automatic_csv_builder |
| Manual replay used? | False |
| Policy source SHA-256 | 1fcdaef3e942c932862a87957c03ae308d89606cdd715046278ee34a484d34d8 |
| Freeze rows SHA-256 | 738101038e03bd8d0fe4b1b24c69907ed5ce561226f758ae115fe64c674fb2a3 |

Boundary: Diagnostic replay only; not an independent estimate of policy effectiveness.
