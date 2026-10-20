# Qwen3 8B V2 recovery status

Date: 2026-09-19
Model: `Qwen/Qwen3-8B`
Attempt: `R1-recovery-context16384-1slot`
Frozen measurement system: commit `ba5ae8fedbf7fe9907dd8ebe985451c04cbf5e1a`

## Outcome

All seven tasks completed with preserved V2 evidence. Deterministic V2
scores are:

| Task | Points |
|---|---:|
| Q01 | 4/10 |
| Q02 | 0/10 |
| Q03 | 0/10 |
| Q04 | 0/10 |
| Q05 | 0/10 |
| Q06 | 0/10 |
| Q07 | 0/20 |
| Total | **4/80** |

No full task objective was completed.

## Resource qualification

The preflight passed with approximately 12 GiB available RAM and only 16 KiB
swap in use. During model loading, swap rose to approximately 339 MiB. The
task-level samples show no positive swap delta within individual tasks, but
the increase occurred while the model was resident and is therefore treated
as model-attributable swap. The repetition is consequently **resource-
ineligible** under the frozen rule, despite minimum task-sample available RAM
remaining above 5 GiB (approximately 5.09 GiB at Q07).

This is preserved behavioral evidence, not a clean resource-qualified primary
observation. No subsequent model run is started until the resource issue is
resolved or explicitly adjudicated.

## Configuration

The valid recovery launch used the ThinkPad Vulkan build at commit
`972d2313bc0bf0a45f634f77d95c9fb03aeab12`, Qwen3 GGUF hash
`d98cdcbd03e17ce47681435b5150e34c1417f50b5c0019dd560e4882c5745785`,
`-ngl 99`, `-c 16384`, `--parallel 1`, temperature 0, seed 0, and max tokens
768. The one-slot configuration was used because the four-slot equivalent
required a 65,536-token total context allocation and was killed during model
loading; that setup attempt is separately preserved as infrastructure-invalid.

## Evidence

Raw task evidence is under
`raw_runs/stage1-v2-recovery/thinkpad/Qwen3-8B/R1-recovery-context16384-1slot/`.
The scored summary is `processed_results/qwen3-v2-recovery-v2.json`.
The prior interrupted attempt and invalid launch setups remain under
`logs/interrupted/`.
