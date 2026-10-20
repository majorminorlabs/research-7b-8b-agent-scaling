# Initial audit

Audit date: 2026-09-19

Reference repository: `<WORKDIR>/tests/mm-4b-benchmark`

Reference commit: `fed50452ffbdb4ca4d84bffd880b760925dc73c4`

The reference repository is clean on `master` and remains read-only for this
study. Its frozen protocol is `qualification-v1.0.0`.

## Frozen benchmark definition

- Seven deterministic simulated operations tasks, Q01–Q07.
- Q01–Q06 are worth 10 points each; Q07 is worth 20; total 80.
- Tasks, tool schemas, initial/hidden state, success conditions, prohibited
  actions, scoring atoms, and score caps are defined in `tasks/fixtures.json`.
- The simulator records tool calls and state transitions.
- Scoring is explicit and deterministic; there is no LLM judge or human
  judgment in v1.
- The frozen termination conditions include verified success, catastrophic or
  prohibited actions where specified, and an invalid-call limit.

## Frozen execution controls

- llama.cpp commit: `972d2313bc0bf0a45f634f77d95c9fb03aeab12`
- Backend: Vulkan/RADV
- Historical hardware: ThinkPad T14 Gen 2a, AMD Ryzen 7 PRO 5850U,
  approximately 14.5 GiB usable RAM, AMD Radeon Graphics (RADV RENOIR)
- Quantization: Q4_K_M GGUF
- Context ceiling: 16,384 tokens
- Generation ceiling: 768 tokens
- Temperature: 0
- Seed: 0 / fixed where supported
- Internet during model runs: disabled
- External tools: deterministic simulator only
- Human intervention: none
- Resource rule: at least 5.0 GiB available RAM, no model-attributable swap,
  and no memory instability

The runner payload independently confirms `max_tokens: 768`,
`temperature: 0`, `seed: 0`, `reasoning_effort: none`, and
`reasoning_format: none`. Native GGUF chat templates were used; Qwen3 used
thinking disabled. The larger-model replay must preserve these semantics
unless a model-specific tokenizer/runtime requirement is documented before
exposure.

## Historical references for paired analysis

| Historical model | Evidence set | Score |
|---|---|---:|
| `mistralai/Ministral-3-3B-Instruct-2512` | three repeated observations | 25/80 each |
| `Qwen/Qwen3-4B` | three repeated observations | 17/80 each |
| `Qwen/Qwen2.5-3B-Instruct` | first round | 14/80 |
| `ibm-granite/granite-4.1-3B` | first round | 12/80 |
| `meta-llama/Llama-3.2-3B-Instruct` | first round | 12/80 |

The historical study also contains Nemotron, but this scaling study does not
include it unless a defensible approximately 7B/8B sibling is identified.
The custom-trained 8B model and its base comparison are explicitly excluded.

## Replay constraints

The historical raw outputs and final results are preserved in the reference
repository and are not modified. This study will store new raw evidence,
failed attempts, retries, manifests, environment records, and derived
results locally under this repository. A failed infrastructure attempt will
remain visible and will not be silently replaced by a retry.

## Initial scientific assessment

Replay is technically well-defined from the copied fixtures, simulator,
scorer, execution configuration, and schedules. The direct pairings still
require upstream variant, revision, quantization, access, and runtime
verification. The Llama pairing is preclassified as cross-generation and
descriptive rather than a controlled parameter-scaling comparison.
