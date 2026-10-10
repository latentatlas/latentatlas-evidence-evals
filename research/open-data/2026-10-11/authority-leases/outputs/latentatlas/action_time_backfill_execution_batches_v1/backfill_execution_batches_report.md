# Action-Time Backfill Execution Batches

Status: `pass`
Generated at: `2026-07-15T17:10:53.720134+00:00`

## Boundary

These files are execution aids only. They do not mark rows independently reviewed, ingest outcomes, compute Level 4 readiness, publish claims, call external services, or mutate production truth.

## Counts

- source queue rows: `2614`
- already completed response rows excluded: `6`
- pending rows batched: `2608`
- batch size: `100`
- batch count: `27`

## Execution Order

1. Send one batch at a time.
2. Require every returned row to include reviewed_outcome, confidence, notes_code, and rationale_short.
3. Keep returned responses in intake, not production truth.
4. Run validation and adjudication before updating any Level 4 summary.
5. Rerun the Level 4 engine after accepted batches are ingested.

## Batch Manifest

| Batch | Rows | Priority counts | Reviewer packet | Response template |
| --- | ---: | --- | --- | --- |
| `backfill_batch_001` | 100 | `{'P0': 100}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_001_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_001_response_template.csv` |
| `backfill_batch_002` | 100 | `{'P0': 45, 'P1': 55}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_002_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_002_response_template.csv` |
| `backfill_batch_003` | 100 | `{'P1': 100}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_003_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_003_response_template.csv` |
| `backfill_batch_004` | 100 | `{'P1': 100}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_004_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_004_response_template.csv` |
| `backfill_batch_005` | 100 | `{'P1': 100}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_005_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_005_response_template.csv` |
| `backfill_batch_006` | 100 | `{'P1': 100}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_006_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_006_response_template.csv` |
| `backfill_batch_007` | 100 | `{'P1': 100}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_007_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_007_response_template.csv` |
| `backfill_batch_008` | 100 | `{'P1': 100}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_008_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_008_response_template.csv` |
| `backfill_batch_009` | 100 | `{'P1': 100}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_009_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_009_response_template.csv` |
| `backfill_batch_010` | 100 | `{'P1': 100}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_010_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_010_response_template.csv` |
| `backfill_batch_011` | 100 | `{'P1': 100}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_011_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_011_response_template.csv` |
| `backfill_batch_012` | 100 | `{'P1': 100}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_012_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_012_response_template.csv` |
| `backfill_batch_013` | 100 | `{'P1': 100}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_013_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_013_response_template.csv` |
| `backfill_batch_014` | 100 | `{'P1': 100}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_014_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_014_response_template.csv` |
| `backfill_batch_015` | 100 | `{'P1': 100}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_015_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_015_response_template.csv` |
| `backfill_batch_016` | 100 | `{'P1': 100}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_016_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_016_response_template.csv` |
| `backfill_batch_017` | 100 | `{'P1': 100}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_017_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_017_response_template.csv` |
| `backfill_batch_018` | 100 | `{'P1': 100}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_018_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_018_response_template.csv` |
| `backfill_batch_019` | 100 | `{'P1': 100}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_019_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_019_response_template.csv` |
| `backfill_batch_020` | 100 | `{'P1': 8, 'P2': 92}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_020_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_020_response_template.csv` |
| `backfill_batch_021` | 100 | `{'P2': 100}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_021_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_021_response_template.csv` |
| `backfill_batch_022` | 100 | `{'P2': 100}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_022_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_022_response_template.csv` |
| `backfill_batch_023` | 100 | `{'P2': 100}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_023_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_023_response_template.csv` |
| `backfill_batch_024` | 100 | `{'P2': 100}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_024_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_024_response_template.csv` |
| `backfill_batch_025` | 100 | `{'P2': 100}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_025_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_025_response_template.csv` |
| `backfill_batch_026` | 100 | `{'P2': 100}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_026_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_026_response_template.csv` |
| `backfill_batch_027` | 8 | `{'P2': 8}` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/batches/backfill_batch_027_reviewer_packet.csv` | `outputs/latentatlas/action_time_backfill_execution_batches_v1/response_templates/backfill_batch_027_response_template.csv` |

## Claim Boundary

- allowed: pending masked backfill rows have been split into controlled execution batches.
- not allowed: claiming the rows are independently reviewed before response intake and adjudication.
