# Qwen3 8B clean V2 replication report

Date: 2026-09-19  
Replication ID: `R2-clean-replication-postreboot`  
Frozen V2 commit: `ba5ae8fedbf7fe9907dd8ebe985451c04cbf5e1a`

## Result

The post-reboot replication completed all seven tasks without transport or
server failure. Frozen V2 scoring produced:

| Task | V2 points |
|---|---:|
| Q01 | 4/10 |
| Q02 | 0/10 |
| Q03 | 0/10 |
| Q04 | 0/10 |
| Q05 | 0/10 |
| Q06 | 0/10 |
| Q07 | 0/20 |
| Total | **4/80** |

Full objectives completed: **0**. V1 continuity scoring was not run; V2 is
the primary endpoint.

## Model and launch

- Model: `Qwen/Qwen3-8B`
- GGUF: `Qwen3-8B-Q4_K_M.gguf`
- SHA-256: `d98cdcbd03e17ce47681435b5150e34c1417f50b5c0019dd560e4882c5745785`
- Quantization: Q4_K_M
- Runtime: llama.cpp `0.4.1-dev`, build 11028,
  commit `972d2313bc0bf0a45f634f77d95c9fb03aeab12`
- Backend/device: Vulkan/RADV, AMD Radeon Graphics (RADV RENOIR)
- Launch: `-ngl 99 -c 16384 -n 768 --temp 0 --seed 0 --parallel 1`
- Thinking: disabled via the frozen Qwen3 execution setting

The server reported `n_slots = 1` and `n_ctx_slot = 16384`. No 65,536-context
or four-slot experiment was performed.

## Resource telemetry

Post-reboot baseline before model load:

- uptime: under one minute;
- physical RAM: 15,154,220 kB (14.46 GiB);
- `MemAvailable`: 12,793,148 kB (12.20 GiB);
- swap total: 19,347,956 kB (18.46 GiB);
- swap used: 0 B; zram used: 0 B;
- `vm.swappiness`: 180;
- memory PSI averages: 0.00 for `some` and `full`;
- no stale llama process.

During the valid run, 616 one-second telemetry samples were preserved:

- initial swap: 0 B;
- final swap: 0 B;
- maximum swap: 0 B;
- valid-run swap delta: 0 B;
- minimum `MemAvailable`: 5,075,623,936 bytes (4.727 GiB);
- peak llama-server RSS: 1,246,629,888 bytes (1.161 GiB);
- peak llama-server virtual size: 10,617,946,112 bytes (9.889 GiB);
- maximum observed RADV VRAM used: 1,017,139,200 of 1,073,741,824 bytes
  (0.947 of the 1 GiB visible heap);
- server `VmSwap`: 0 throughout sampled residency;
- memory PSI remained 0.00 during the run;
- OOM-kill counter remained 0 and swap-in/swap-out counters did not increase
  during the captured run.

The frozen resource verdict is **FAIL** because minimum available RAM fell
below the 5.0 GiB threshold, despite zero swap growth and no memory PSI/OOM
signal.

## Comparisons

- Preserved contaminated-baseline Qwen3 8B observation: **4/80**, resource
  ineligible due to contaminated swap history.
- Clean post-reboot Qwen3 8B replication: **4/80**, resource ineligible due
  to the 4.727 GiB minimum available-RAM observation.
- Historical Qwen3 4B V2 results: **0/80** in each of three repetitions;
  those historical resource labels remain separate from this result.

The clean replication does not establish a resource-eligible 8B scaling
improvement. It reproduces the prior V2 point total under a clean zero-swap
baseline, but the larger model still crosses the frozen RAM floor during the
workload.

## Artifacts

- Raw tasks:
  `raw_runs/stage1-v2-replication/thinkpad/Qwen3-8B/R2-clean-replication-postreboot/`
- Pre-load and post-load snapshots:
  `logs/server/R2-clean-replication-postreboot/preflight-before-load.txt` and
  `post-load.txt`
- Continuous telemetry:
  `logs/server/R2-clean-replication-postreboot/resource-telemetry.jsonl`
- Server log:
  `logs/server/R2-clean-replication-postreboot/server.log`
- Deterministic V2 summary:
  `processed_results/qwen3-v2-clean-replication-v2.json`
- Scoring/summary script:
  `analysis/score_v2_clean_replication.py`

No Qwen2.5 7B or other model was started after this replication.
