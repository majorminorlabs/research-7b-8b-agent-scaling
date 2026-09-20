# Methodology and scoring closeout note

The historical V1 traces were audited after the original benchmark because V1 totals could award points for action patterns that did not establish the intended outcome. V2 is the frozen outcome-first correction: it scores preserved simulator events against explicit success predicates, state transitions, safety constraints, and termination conditions. V2 does not rerun models or infer missing behavior from prose. V1 and V2 scores remain separate and must not be collapsed into one measure.

The primary final evidence uses the controlled Mac/Metal cohort because the Qwen3 bridge showed material behavioral divergence between ThinkPad/Vulkan and Mac/Metal despite frozen task semantics and the same llama.cpp commit. Historical ThinkPad/Vulkan runs are retained as contextual evidence only.

The final Mac runs use V2 scorer `v2.0.0`, simulator `v2.0.0`, one slot, 16,384 context, temperature 0, seed 0, maximum generation 768, and llama.cpp `972d2313bc0bf0a45f634f77d95c9fb03aeab12`. Resource eligibility uses the frozen 5 GiB available-memory/no-model-attributable-swap rule. The corrected Mac collector samples the actual llama-server child PID, RSS, memory pressure, vm_stat, and swapusage.

Canonical score reproduction uses each preserved task's `result.json`, `simulator-events.json`, and `final_answer` with `scoring.v2.core.score_run` and the frozen task fixtures. No raw evidence was rewritten.
