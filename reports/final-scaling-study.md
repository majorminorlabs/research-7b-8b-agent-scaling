# Final Mac/Metal 7B/8B sibling-scaling study

Status: complete. Final evidence commit is recorded after repository audit. No Llama or other unplanned model was launched.

## Final conclusion

Under the frozen V2 benchmark, on the controlled Mac Studio M1 Max / Metal environment, no larger sibling outperformed its smaller sibling in the four same-family pairs. Qwen3 and Granite 4.1 tied; Qwen2.5 and Ministral scored lower at the larger size. The two informative pair differences were reproduced exactly in R2: Ministral 3B's Q05 success recurred, and the Qwen2.5 3B > 7B difference recurred. All 12 Mac model-runs completed zero full objectives.

This supports a narrow conclusion: **no positive parameter-scaling signal was observed for these artifacts and these agentic tasks in this environment**. It does not support the broader claims that larger models are generally worse or that parameter scaling has no value generally.

## Experimental history

The project began with continuation of the 3B/4B and 7B/8B work on ThinkPad/Vulkan. The V1 scorer audit showed that the original outcome interpretation was not reliable, so the frozen V2 scorer was adopted to score preserved simulator outcomes and explicit success predicates. The ThinkPad then exposed a resource-floor problem for Qwen3 8B: the model could run but fell below the frozen available-RAM rule. A clean Qwen3 Mac/Metal bridge was established after artifact recovery and showed material behavioral divergence from ThinkPad/Vulkan. The primary study was therefore moved to a separately identified, controlled Mac/Metal cohort rather than pooling backends.

## Primary results

| Family | Small | Large | R1 scores | R2 scores | Mean Δ large−small | Replication result |
|---|---:|---:|---|---|---:|---|
| Qwen3 | 4B | 8B | 4 → 4 | — | 0 | single pair, tied |
| Qwen2.5 | 3B | 7B | 4 → 0 | 4 → 0 | −4 | exact score vectors reproduced |
| Granite 4.1 | 3B | 8B | 5 → 5 | — | 0 | single pair, tied |
| Ministral 3 | 3B | 8B | 10 → 2 | 10 → 2 | −8 | exact score vectors reproduced; Q05 reproduced |

Aggregate across the original four Mac pairs was 23/320 for smaller siblings versus 11/320 for larger siblings; larger > smaller occurred 0/4, ties 2/4, and larger < smaller 2/4. These are descriptive results from four families, not inferential estimates.

## Replication findings

### Ministral 3

The R1 3B Q05 outcome reproduced exactly in R2: compatible `j-cpu` work was moved to node-c while GPU-affine `j-gpu` was retained, earning 8 points. The 8B scored 0 on Q05 in both runs. The full score vectors were identical across repetitions for both models. This is stable evidence for the observed pair difference under this protocol, but artifact provenance differs: the 3B is a Bartowski imatrix Q4_K_M artifact and the 8B is an official Mistral Q4_K_M artifact.

### Qwen2.5

The 3B scored 4 and the 7B scored 0 in both repetitions, with identical per-task vectors R1↔R2. The difference is therefore not a one-run anomaly in this cohort. It is still a task-specific result: the 3B repeatedly earned Q01 named-deployment credit while the 7B repeatedly selected a generic/prohibited path.

## Core questions

1. **Did any larger sibling outperform?** No, not in the four controlled pairs.
2. **Did any larger sibling cross a missing capability threshold?** No. No full objective was completed and no new capability threshold appeared at the larger size.
3. **Did any model complete a full objective?** No: 0/12 Mac model-runs.
4. **Were apparent regressions stable?** Yes for the two replicated pairs: both score differences reproduced exactly.
5. **Were larger models more resource-intensive?** Yes. In the three pairs with corrected paired RSS/throughput telemetry, larger siblings used about 1.76×–2.23× peak server RSS and generated approximately 49%–51% more slowly.
6. **Did parameter count improve agentic execution here?** No positive improvement was observed under this benchmark/environment/artifact set. This is not a general scaling claim.

## Task difficulty and behavior

Most credit remained concentrated in Q01. Across the original eight Mac runs, Q01 contributed 26 points; Q05 contributed 8, all from Ministral 3B; Q02, Q03, Q04, Q06, and Q07 contributed zero. Q01 shows partial deployment behavior but not reliable end-to-end completion because later invalid or unsafe actions often cap the score. Q05 provides the clearest genuine safe state-change evidence.

Failures clustered around multi-step planning, tool-argument/API selection, state verification, safety boundaries, and final task completion. Larger models often changed the action sequence—more diagnostics, replacement attempts, retries, or mutations—without changing the scored outcome. The zero full-objective count makes the benchmark extremely difficult for this model range and creates a floor/ceiling-of-difficulty concern: partial V2 points discriminate behavior, but the end-to-end objective remains out of reach.

An intermediate-difficulty successor benchmark is justified as future work if the research question requires more full-objective observations. That would be a new benchmark, not a retrospective weakening of this frozen one.

## Efficiency and resources

| Pair | R1 peak RSS small → large | R2 peak RSS small → large | R1/R2 generation tok/s small → large | Eligibility |
|---|---|---|---|---|
| Qwen2.5 | 2.953 → 5.780 GiB | 2.951 → 5.782 GiB | R1 78.30 → 39.98; R2 76.82 → 39.56 | PASS / PASS |
| Granite 4.1 | 3.862 → 8.622 GiB | — | 68.00 → 33.45 | PASS / PASS |
| Ministral 3 | 4.465 → 7.872 GiB | 4.460 → 7.873 GiB | R1 71.06 → 34.60; R2 71.31 → 34.59 | PASS / PASS |

All completed Mac runs were resource-eligible with zero swap and zero swap I/O. Qwen3 8B's earlier server RSS was not recoverable because its collector tracked the task-loop shell PID; that limitation is preserved and no paired Qwen3 efficiency claim is made. Efficiency is reported separately from capability. The R2 telemetry is close to R1 for both replicated pairs, supporting comparable execution conditions.

## Methodological limitations

- The Mac/Metal cohort is intentionally not pooled with historical ThinkPad/Vulkan traces because the bridge showed material backend/runtime behavioral divergence. ThinkPad scores remain contextual only.
- The Ministral pair has different artifact provenance in addition to different parameter counts.
- Qwen3 and Granite have one repetition per model; only Qwen2.5 and Ministral have R2 confirmation.
- Absolute scores are low and full objectives are absent.
- The benchmark measures these frozen agentic tasks and artifacts, not general intelligence.
- Deterministic settings do not remove backend, runtime, artifact, or execution-environment effects.

## Llama decision and study closeout

Llama 3.2 3B → Llama 3.1 8B was omitted. It is cross-generation rather than a clean same-generation sibling pair, and would not materially strengthen the core same-family conclusion at this closeout stage. It may be run later only as explicitly labeled supplemental evidence.

The core study is closed. No additional repetitions are required under the defined stop rule. The most useful future work is either a planned replication of Qwen3/Granite or an intermediate-difficulty benchmark designed to produce more complete objectives.

## Canonical artifacts

- [Canonical JSON results](../results/canonical-results-v1.json)
- [Compact CSV summary](../results/pair-summary.csv)
- [Final manifest](../manifests/model-run-manifest.json)
- [V1→V2 methodology note](../methodology/v1-to-v2.md)
- [Final status README](../LOCAL_STATUS.md)
- [Interim synthesis, preserved and superseded](../reports/final-scaling-study.md)

Raw evidence remains under `raw_runs/stage1-v2-mac-metal/` and was not rewritten.
