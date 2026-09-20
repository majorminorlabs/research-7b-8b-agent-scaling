# MAJOR//minor 7B/8B scaling study — final status

Status: **complete for the defined Mac/Metal core cohort**.

The study contains four controlled same-family pairs. Qwen2.5 and Ministral received one additional R2 repetition each for the two informative R1 findings. The R2 score vectors exactly matched R1 for all four replicated models. Ministral 3B's Q05 safe state change reproduced; the Qwen2.5 3B > 7B score difference reproduced.

No Llama run was launched. Llama 3.2 3B → Llama 3.1 8B was omitted from core evidence because it is cross-generation and would not strengthen the clean same-family conclusion enough to justify changing the defined closeout scope. It remains possible supplemental future work.

No raw runs, historical reports, V1 scores, benchmark tasks, prompts, simulator semantics, scorer, or resource rule were changed. The interim report is superseded for status purposes by `reports/FINAL_MAC_METAL_SCALING_STUDY_V1.md`, but remains preserved.

Canonical artifacts:

- `reports/FINAL_MAC_METAL_SCALING_STUDY_V1.md`
- `processed_results/mac_scaling_final_results_v1.json`
- `processed_results/mac_scaling_final_summary.csv`
- `reports/METHODOLOGY_V1_TO_V2_CLOSEOUT_NOTE.md`
- `manifests/mac_scaling_final_manifest_v1.json`
