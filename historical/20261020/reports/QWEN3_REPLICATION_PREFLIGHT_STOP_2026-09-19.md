# Qwen3 8B clean-replication preflight stop

Date: 2026-09-19  
Host: ThinkPad T14 Gen 2a / `pop-os`  
Frozen runtime: `0.4.1-dev (build 11028, commit 972d2313b)`  
Model: `Qwen3-8B-Q4_K_M.gguf`  
Model SHA-256: `d98cdcbd03e17ce47681435b5150e34c1417f50b5c0019dd560e4882c5745785`

## Decision

**Stopped before model loading.** No replication was launched.

The host is reachable and otherwise healthy, but the requested uncontaminated
baseline is not present. Swap remains materially occupied from the previous
failed launch episode:

- total RAM: 15,154,216 kB (14.46 GiB; `free -h` rounds to 14 GiB);
- `MemAvailable`: 13,037,944 kB (12.43 GiB);
- swap total: 19,347,956 kB (18.46 GiB);
- swap used: 316,016 kB (308.61 MiB), all on `/dev/zram0`;
- `/dev/dm-0`: 4,193,784 kB, 0 used;
- `/dev/zram0`: 15,154,172 kB, 316,016 kB used;
- `vm.swappiness`: 180.

This is not a clean post-failure baseline. No swap was cleared, no caches were
dropped, and no kernel setting or unrelated process was changed.

## Read-only health observations

- Uptime: 1 hour 53 minutes at `2026-09-19 21:10:44 CDT`.
- Memory PSI: `avg10=0.00`, `avg60=0.00`, `avg300=0.00` for both `some` and
  `full` memory pressure.
- I/O PSI: `avg10=0.00`, `avg60=0.00`, `avg300=0.00` for both `some` and
  `full` pressure.
- No stale `llama-server` or `llama-cli` process was present.
- The largest ordinary processes were desktop COSMIC components, each below
  100 MiB RSS; no unrelated process was individually material relative to the
  available memory.
- Vulkan reports AMD Radeon Graphics (RADV RENOIR), Mesa RADV 25.2.8, with
  llvmpipe also available. No live model GPU allocation exists because no
  model was loaded; no VRAM telemetry tool was installed and DRM memory files
  were unavailable.

## Relevant `/proc/meminfo` snapshot

```text
MemTotal:       15154216 kB
MemFree:        10665336 kB
MemAvailable:   13037944 kB
Buffers:           16472 kB
Cached:          3313528 kB
SwapCached:          864 kB
Active:           295128 kB
Inactive:        3284512 kB
Active(anon):      79268 kB
Inactive(anon):   215648 kB
Active(file):     215860 kB
Inactive(file):  3068864 kB
Unevictable:       10808 kB
Mlocked:           10808 kB
SwapTotal:      19347956 kB
SwapFree:       19031940 kB
Zswap:                 0 kB
Zswapped:             0 kB
Dirty:               936 kB
Writeback:             0 kB
AnonPages:        259520 kB
Mapped:           361036 kB
Shmem:             36532 kB
KReclaimable:      42196 kB
Slab:             252352 kB
SReclaimable:      42196 kB
SUnreclaim:       210156 kB
KernelStack:       18964 kB
PageTables:        19420 kB
SecPageTables:      3852 kB
NFS_Unstable:          0 kB
Bounce:                0 kB
WritebackTmp:          0 kB
AnonHugePages:      32768 kB
ShmemHugePages:         0 kB
FileHugePages:      63488 kB
CmaTotal:               0 kB
CmaFree:          1914284 kB
HardwareCorrupted:      0 kB
VmallocUsed:       152284 kB
CommitLimit:     26925064 kB
Committed_AS:     3398712 kB
oom_kill:              20
```

## Frozen launch checks not reached

The model identity/hash and frozen runtime identity were verified without
loading the model. The intended replication would use Q4_K_M, Vulkan/RADV,
one slot, 16,384-token context per slot, temperature 0, seed 0, and max 768
tokens. Because the swap baseline is contaminated, no launch configuration
was exercised and no replication ID was consumed.

## Resume condition

Do not modify the host to manufacture eligibility. Resume only when the host
naturally presents a clean, reproducible baseline acceptable under the frozen
rule, then repeat this read-only preflight and record the baseline immediately
before model loading.
