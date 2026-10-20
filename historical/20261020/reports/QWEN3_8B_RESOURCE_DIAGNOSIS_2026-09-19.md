# Qwen3 8B V2 resource diagnosis

Date: 2026-09-19  
Scope: read-only diagnosis only; no model was launched and the host was not modified.  
Run preserved: `R1-recovery-context16384-1slot`  
Frozen rule: `ba5ae8fedbf7fe9907dd8ebe985451c04cbf5e1a`

## Diagnosis

Most likely cause: the approximately 339 MiB of swap was created during or
after the preceding invalid 65,536-total-context Qwen3 launch, which was killed
during model loading. It was not created by the valid seven-task Qwen3 run.

The timeline is decisive:

1. Before the invalid launch: approximately 12 GiB available RAM and 16 KiB
   swap used.
2. Invalid launch: `-c 65536 --parallel 4 -ngl 99`; llama.cpp reported
   `failed to fit params to free device memory`, then the server was killed.
3. Before the valid run: approximately 12 GiB available RAM but 358 MiB swap
   already used.
4. Valid run: one slot, `-c 16384`; task samples began at 359 MiB swap and
   swap stayed flat or declined to 341 MiB by Q07.

Thus the earlier report’s shorthand “16 KiB before model loading to 339 MiB
with the model resident” conflated two launch attempts. The valid run’s own
baseline was already approximately 358 MiB.

## Requested resource findings

### 1. Physical and available RAM

The frozen protocol identifies the ThinkPad as having 14.5 GiB usable RAM.
The valid-run preflight reported 14 GiB total and approximately 12 GiB
available using `free -h`. An exact pre-load `MemAvailable` value was not
recorded by that preflight. The valid task samples fell from 6.07 GiB at Q01
to 5.09 GiB at Q07.

### 2. Model size and approximate resident requirement

The Qwen3 GGUF is 5,027,783,488 bytes (4.682 GiB; 5.028 GB), hash
`d98cdcbd03e17ce47681435b5150e34c1417f50b5c0019dd560e4882c5745785`.

The preserved server-process RSS rose from approximately 0.16 GiB at Q01 to
1.16 GiB at Q07. This is not the complete model footprint because the run used
Vulkan offload and the weight file/GPU allocations are not represented by
ordinary process RSS.

### 3. RSS, virtual memory, mapped files, GPU allocation

Preserved evidence contains server RSS only; the historical sampler records
`ps` RSS and `/proc/meminfo`. It does not contain `VmSize`, `VmRSS` from a
resident process snapshot, `smaps_rollup`, mapped-file totals, page faults, or
Vulkan allocation telemetry. The server log records model load and
`n_ctx_slot = 16384`, but no buffer-size or VRAM allocation breakdown.

The server was stopped after completion, and the ThinkPad later became
unreachable, so those live `/proc` and GPU values cannot be recovered without
another resident model (which this phase explicitly forbids).

### 4. Proactive paging versus actual pressure

The valid run shows no task-time swap growth, no OOM/allocation error, no
transport failure, no context truncation, and all seven tasks completed.
Available RAM remained above 5 GiB in every task sample. This strongly argues
against benchmark-affecting memory pressure during the valid run.

The swap increase is more consistent with kernel/zram page management around
the failed large-context allocation, potentially evicting cold anonymous
pages. It cannot be proven to be purely proactive paging because the relevant
run-time PSI, `vmstat`, `vm.swappiness`, and process/cgroup snapshots were not
captured.

### 5–7. Swappiness, swap configuration, and `/proc/meminfo`

The preserved preflight recorded an 18 GiB total swap configuration but did not
record `vm.swappiness` or the exact swap devices. Earlier health output showed
`/dev/dm-0` (4 GiB) and `/dev/zram0` (14.5 GiB). The ThinkPad was unreachable
for the requested read-only retry, so the current swappiness and full live
`/proc/meminfo` cannot be reported. No setting was changed.

### 8. Background processes

The valid preflight found no stale llama server. The preserved Qwen task
samples do not include a process-tree census or host-wide RSS list. No evidence
shows a materially consuming benchmark-side background process, but this cannot
be established for unrelated desktop processes from the saved records.

### 9. Does 339 MiB indicate genuine benchmark pressure?

Not for the valid Qwen3 task execution, based on available evidence. The
increase happened before the valid run’s baseline; during that run swap
decreased, RAM stayed above the floor, RSS remained modest, and execution
completed normally. It is evidence of host paging/resource history, not proof
that Qwen3’s behavioral score was degraded by memory pressure.

## Frozen eligibility rule

The rule requires all of the following:

- `MemAvailable >= 5.0 GiB` throughout;
- zero model-attributable/inference swap;
- no memory-related instability;
- baseline swap must be distinguished from inference swap.

The Qwen3 recovery was conservatively marked resource-ineligible because its
clean 16 KiB baseline was contaminated by the immediately preceding failed
launch, and the resulting swap increase could not be attributed with the
required certainty. The valid run itself has zero positive task-level swap
delta, but that does not retroactively repair the contaminated launch history.

## Historical consistency

Historical 3B/4B runs used the same basic measurement fields: `MemAvailable`,
`SwapTotal`, `SwapFree`, and server RSS. Historical task samples generally had
zero within-run swap delta, but the machine already had approximately 2.0–2.1
GiB swap in use. The historical forensic report also records a broader swap
jump during the first-round qualification loop whose attribution was not
captured; that first round therefore could not certify resource eligibility.

Historical finalist examples:

- Ministral 3B: minimum available RAM about 6.04 GiB in repetitions; zero
  task-level swap delta.
- Qwen3 4B: minimum available RAM about 4.953 GiB across finalist
  repetitions; zero task-level swap delta, but resource FAIL on the RAM floor.
- The historical resource rule was therefore already a separate eligibility
  axis rather than a deletion rule for capability points.

The new Qwen3 8B record is consistent in measurement fields, but has a better
documented launch-attempt boundary than the historical first-round swap
timeline. Historical capability comparisons should not be described as
uniformly resource-qualified without retaining those limitations.

## Can this hardware run the cohort under the frozen rule?

Conditionally, yes, but not yet demonstrated for a clean 7B/8B observation.
The Qwen3 8B model loaded and completed the workload with more than 5 GiB
available during tasks and no task-time swap growth. The present run cannot be
certified because its clean baseline was lost to the preceding failed launch.

The safest protocol-compliant future path is a separately identified run after
a clean host baseline (ideally a fresh boot or otherwise naturally clean
state), with no failed large-context attempt beforehand; record exact
`/proc/meminfo`, `vm.swappiness`, `/proc/swaps`, process RSS/`smaps_rollup`,
page-fault/PSI counters, process-tree RSS, and Vulkan allocation telemetry
before load, after load, throughout tasks, and after exit. Use only a
configuration that reports `n_ctx_slot = 16384` and stop before evidence if
swap becomes model-attributable. This does not change the scorer, benchmark, or
resource rule.

## Conclusion

The 339 MiB swap figure is most plausibly a consequence of the failed
large-context setup and ordinary kernel page management, not genuine memory
pressure affecting the completed Qwen3 behavior. The run remains preserved as
resource-ineligible under the frozen adjudication because attribution was not
cleanly established. No historical raw evidence was changed, and no new model
run was started.
