# 7B/8B hardware migration audit

Date: 2026-09-19  
Scope: read-only audit; no model launched and no frozen benchmark/scorer/resource rule changed.

## Recommendation

Use the Mac Studio M1 Max, 32 GiB unified memory, as the least disruptive practical target for the remaining 7B/8B capability cohort, subject to a new, explicitly identified migration cohort and a bridge run. Do not describe its results as direct ThinkPad/Vulkan replications. The ThinkPad is the only observed environment matching the frozen hardware/backend definition, but Qwen3 8B has now failed its frozen 5 GiB available-RAM floor on a clean zero-swap run (minimum 4.727 GiB), so it is not a valid target for the remaining large-model runs.

The Windows RTX 3070 node is technically capable and has ample system RAM, but it is methodologically less attractive: it introduces Windows, CUDA or a non-RADV Vulkan implementation, NVIDIA driver behavior, and a different CPU architecture/host configuration. It also has no discoverable `llama-server` installation in the inspected PATH or common directories. Rented hardware is not necessary unless strict ThinkPad/Vulkan/RADV comparability is non-negotiable; in that case, rent an AMD/Linux/Vulkan/RADV-equivalent host with materially more RAM rather than a generic CUDA instance.

## What the frozen protocol requires

The frozen measurement commit is `ba5ae8fedbf7fe9907dd8ebe985451c04cbf5e1a`; the frozen llama.cpp identity is `972d2313bc0bf0a45f634f77d95c9fb03aeab12`. The protocol explicitly fixes the benchmark tasks, prompts/system prompts, deterministic simulator, scoring, no-human-intervention/no-internet conditions, Q4_K_M model requirement, 16,384-token context ceiling, temperature 0, seed 0, and the resource rule: at least 5 GiB available RAM throughout, no model-attributable inference swap, and distinguish baseline swap from run-attributable swap.

The protocol's hardware block also records the reference host, CPU, usable RAM, OS, GPU, and `Vulkan/RADV` backend. It contains no migration clause that makes a different host/backend an equivalent direct replication. Therefore:

| Classification | Variables |
|---|---|
| A — keep identical for a strict direct comparison | tasks/prompts/tools/scorer/simulator; model identity, GGUF hash and Q4_K_M; frozen llama.cpp commit; native chat-template behavior and request fields; Vulkan/RADV backend; 16,384 context; one slot for the V2 server; temperature 0, seed 0, max generation 768; no internet/human intervention; frozen resource rule |
| B — may differ only as a declared migration variable | physical host, OS, CPU architecture, GPU/unified or discrete memory, and backend. Such a run is a new environment/cohort, not a strict historical replication. Record exact host, driver, build, device placement and all launch flags. |
| C — primarily performance/resource variables, but not guaranteed capability-neutral | thread count, mmap, batch/KV settings, GPU-layer offload, VRAM use, prompt/generation tok/s, wall time, RSS, swap and available RAM. Keep them matched where possible; report performance separately from V2 capability points. |
| D — ambiguous in the frozen record | exact thread count, mmap and batch/KV flags; exact offload/tensor placement; whether one-slot is a protocol-wide requirement or the V2 replication configuration; complete server build metadata; cross-backend numerical equivalence; the effect of host migration on resource qualification. |

The safe interpretation is conservative: do not silently relax any A item. A different backend/build/architecture may produce deterministic output on that machine, but temperature 0 and seed 0 do not guarantee cross-backend identity. Floating-point reduction order, GPU kernels, offload partitioning, compiler/driver behavior, tokenizer/template implementation, and llama.cpp changes can alter greedy choices. This is a behavioral confound, not merely a speed difference.

## Target inspection

### Mac Studio

Read-only inspection identified `Mac13,1`, Apple M1 Max (24-core GPU), 32 GiB memory, macOS 26.6.2, Darwin arm64. The installed `/opt/homebrew/bin/llama-server` is version 0.4.1 build 10964, commit `b29c606e2`, built for AppleClang/Darwin arm64. The supported native backend is Metal, not Vulkan/RADV. The machine has sufficient memory headroom in principle for Q4_K_M 7B/8B models and 16,384 context, but the installed llama.cpp is not the frozen commit.

Expected methodological differences: Metal kernels and Apple unified-memory allocation; arm64 numerical/compiler behavior; a different llama.cpp build; and potentially different tensor offload and memory accounting. Exact GGUF files can be used unchanged if present/copied into the isolated project, and llama.cpp's native GGUF templates are the likely route for Qwen3/Qwen2.5/Granite/Llama, but template behavior must be verified and recorded before any run.

Verdict: valid practical migration target; not a strict direct-comparison target without controls.

### Windows RTX 3070 node

Read-only SSH inspection reached `DESKTOP-CKR71I3`, Windows 10 build 22621. It reports 34,279,411,712 bytes physical RAM (about 31.9 GiB) and an NVIDIA GeForce RTX 3070 with 8,192 MiB VRAM, driver 591.86. `vulkaninfo.exe` and `nvidia-smi.exe` are present. No `llama-server` command or executable was found in PATH or the inspected common directories; no installation or dependency was added.

This node should be able to maintain the 5 GiB system-RAM floor for Q4_K_M 7B/8B inference, but exact context/KV and offload feasibility remain unverified. CUDA would be the natural backend; Windows Vulkan would not reproduce Linux RADV. Exact model files and native templates are technically usable, but the frozen commit/build and one-slot launch still need a non-mutating installation/provenance audit before execution.

Verdict: technically plausible but higher migration risk than the Mac Studio and currently not execution-ready.

### ThinkPad

The ThinkPad remains Pop!_OS 24.04, x86_64 Ryzen 7 PRO 5850U, AMD Radeon/RADV, approximately 14.5 GiB usable RAM, and the frozen Vulkan/RADV runtime. It is the closest methodological match. However, the clean Qwen3 8B replication reached only 4.727 GiB minimum available RAM with zero swap and zero PSI, so it fails the frozen RAM floor solely on capacity margin. No more Qwen3 8B runs should be attempted there; using it for the remaining 7B/8B cohort would predictably risk the same eligibility failure.

### Rented hardware

No rented provider or host was connected for inspection. A generic rented GPU is not automatically protocol-compliant. It is necessary only if strict reference-environment comparability is required and an AMD/Linux/RADV host with enough RAM is unavailable. A CUDA rental would have the same backend confound as the RTX node and should be treated as a migration cohort.

## Bridge/control design

Because Metal or CUDA changes numerical execution, a bridge is required before interpreting migrated scores against historical 3B/4B traces. The minimum bridge is one complete Qwen3 4B V2 repetition on the selected new target, using the unchanged Q4_K_M GGUF, frozen prompts/scorer/simulator, exact 16,384 context, one slot, temperature 0, seed 0, max 768, and fully captured resource telemetry. Compare it with the preserved ThinkPad Qwen3 4B 0/80 observations.

The stronger, still minimal design adds one complete historical 3B control (preferably Qwen2.5 3B or Ministral 3B) on the same new target. If either control shows materially different tool formatting, template behavior, or V2 outcomes, report the migrated 7B/8B results as target-specific and do not make a scale-only claim. Do not run these controls until the migration plan is approved.

## Execution plan after review

1. Freeze and verify the selected target's OS, architecture, GPU/backend, driver, llama.cpp commit/build, model hashes, native `/props`/template behavior, launch flags, one-slot/16,384-context configuration, and no-internet state.
2. Capture a clean pre-model baseline: uptime, RAM, `/proc/meminfo` or platform equivalent, swap, PSI where available, process RSS, GPU memory, and exact host state.
3. Run the bridge control(s) first under new replication IDs. Preserve their raw requests/responses, server logs, simulator events, and continuous telemetry. Score with the unchanged V2 scorer.
4. If controls are interpretable, run Qwen3 8B, Qwen2.5 7B, and Granite 7B/8B as separately identified migration replications, in that order, stopping for review after Qwen3 if requested. Eventually run Llama under the same migrated protocol. Never merge migrated artifacts with ThinkPad cohort directories.
5. Treat each model's resource verdict independently. A migration target must still satisfy the frozen 5 GiB available-RAM floor, zero attributable inference swap, and no memory instability; a larger host does not waive the rule.
6. Keep prompt-processing tok/s, generation tok/s, wall time, RSS, GPU memory and host resource use as secondary environment-dependent measurements. Compare them only within the same target/backend or with explicit normalization; do not use them as capability-score evidence.

## Historical-comparison conclusion

The historical 3B/4B traces were collected on the ThinkPad/Vulkan/RADV family and already have resource-record limitations, including pre-existing swap and incomplete per-run attribution in the first round. They remain preserved evidence. A Mac Metal or Windows CUDA/Vulkan cohort can be scientifically useful as a controlled continuation, but it cannot erase those limitations or be presented as a pure hardware-neutral scaling comparison. The bridge controls are the minimum needed to estimate whether the migration changes behavior independently of model size.

No model was launched, no host setting was changed, and no frozen benchmark artifact was modified for this audit.
