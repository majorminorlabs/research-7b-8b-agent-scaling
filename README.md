# MAJOR//minor 3B/4B → 7B/8B sibling-scaling study

This repository publishes the completed, frozen evidence package for a controlled agentic benchmark study. The canonical source was local commit `6e80566ef9487f3b7b592eee621d3bc27af52108` of the private research workspace; this public repository is a curated release derived from that source.

## Result in one sentence

Across four controlled Mac/Metal sibling comparisons, moving from approximately 3B/4B to 7B/8B did not produce a positive scaling signal on this agentic benchmark.

| Family | Smaller | Larger | Result |
|---|---:|---:|---|
| Qwen3 | 4/80 | 4/80 | Tie |
| Qwen2.5 | 4/80 | 0/80 | Larger sibling lower; reproduced |
| Granite 4.1 | 5/80 | 5/80 | Tie |
| Ministral 3 | 10/80 | 2/80 | Larger sibling lower; reproduced |

The larger sibling outperformed in 0/4 families. No full objective was completed in any of the 12 Mac model-runs. The Ministral 3B Q05 safe state change reproduced in R2, as did the Qwen2.5 3B-versus-7B regression. Where paired telemetry was available, larger models used approximately 1.76×–2.23× peak RSS and generated approximately 49%–51% more slowly.

These are narrow observations about these model artifacts, tasks, and execution environment. They do not show that small models are generally better, that 8B models are generally worse, or that scaling has no value.

## What changed methodologically

The work began as a continuation of the earlier [3B/4B benchmark](https://github.com/MAJORminorStudio/4b-agent-model-benchmark). An audit found that the original V1 scorer could reward proxy behavior such as tool activity without sufficiently establishing achieved outcomes. An outcome-first V2 scorer was frozen before the controlled cohort. The ThinkPad/Vulkan environment also failed the frozen memory qualification for Qwen3 8B. A byte-identical Qwen3 4B bridge then showed material behavioral divergence between ThinkPad/Vulkan and Mac/Metal. Historical Vulkan results are therefore contextual only; the primary scaling estimate uses same-environment Mac/Metal pairs.

## Reproduce or inspect

- [Final report](reports/final-scaling-study.md)
- [Canonical machine-readable results](results/canonical-results-v1.json)
- [Pair summary CSV](results/pair-summary.csv)
- [Model/run manifest](manifests/model-run-manifest.json)
- [V1 → V2 methodology note](methodology/v1-to-v2.md)
- [V1 scorer audit](results/v1-scorer-audit.json)
- [Frozen task fixtures](benchmark/tasks/fixtures.json)
- [Frozen V2 scorer and simulator](benchmark/scoring/v2/)
- [Execution and telemetry code](benchmark/execution/)

Model GGUF files are not redistributed. Their filenames, quantizations, source provenance, revisions, byte sizes, and SHA-256 identities are recorded in the manifest and provenance files. The public package contains benchmark definitions, scoring code, canonical results, and enough metadata to inspect the claims without downloading weights.

Raw local evidence is intentionally not mirrored wholesale: preflight/process snapshots contain private host paths and machine-specific process details. The complete raw evidence remains preserved in the canonical local repository; the published JSON/CSV results and scorer inputs are the public evidence layer.

## Scope and limitations

The cohort used one Mac Studio M1 Max, Metal, llama.cpp commit `972d2313bc0bf0a45f634f77d95c9fb03aeab12`, one inference slot, a 16,384-token context, frozen prompts/tool schemas/sampling, and V2 scoring. There was one run per Qwen3 and Granite model and two repetitions per Qwen2.5 and Ministral model. Ministral 3B uses a Bartowski imatrix Q4_K_M artifact while Ministral 8B uses an official Mistral Q4_K_M artifact. Llama was omitted from core evidence because the available comparison would be cross-generation rather than a clean sibling pair.

The benchmark measures these seven simulated agentic tasks, not general model intelligence. Most credit concentrated in Q01; Ministral 3B's Q05 trace was the clearest genuine state change; Q02/Q03/Q04/Q06/Q07 remained unsolved in the published Mac cohort.

## Citation

MAJOR//minor, *3B/4B → 7B/8B sibling-scaling study*, canonical source commit `6e80566ef9487f3b7b592eee621d3bc27af52108`.
