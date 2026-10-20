# Qwen3 4B Mac/Metal bridge preflight stop

Date: 2026-09-20  
Workspace: `<WORKDIR>/tests/mm-8b-benchmark`  
Bridge identity reserved: `QWEN3-4B-MAC-METAL-BRIDGE-R1`

## Decision

The bridge was **not run**. Classification: **D — invalid/inconclusive** for bridge comparability because the exact historical Qwen3 4B GGUF could not be verified on the Mac and the Mac did not present a clean resource baseline. No 8B or other model was launched.

## Exact frozen llama.cpp build

The frozen source was cloned into the isolated runtime directory and detached at:

`972d2313bc0bf0a45f634f77d95c9fb03aeab12`

The first configuration attempt ran under the terminal's Rosetta/x86_64 architecture and failed with `unknown target CPU 'apple-m1'`; it produced no usable binary. This was corrected by invoking the unchanged source/toolchain natively with `arch -arm64`, `GGML_NATIVE=OFF`, and `CMAKE_OSX_ARCHITECTURES=arm64`.

The exact commit then built successfully with Metal:

```text
cmake -S runtime/llama.cpp-972d2313b -B runtime/llama.cpp-972d2313b/build-metal-arm64 \
  -DGGML_METAL=ON -DGGML_NATIVE=OFF -DCMAKE_OSX_ARCHITECTURES=arm64 \
  -DLLAMA_BUILD_SERVER=ON -DLLAMA_CURL=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build runtime/llama.cpp-972d2313b/build-metal-arm64 \
  --target llama-server llama-cli -j 8
```

CMake reported `CMAKE_SYSTEM_PROCESSOR: arm64`, `GGML_SYSTEM_ARCH: ARM`, `Including METAL backend`, and `ggml commit: 972d2313b`. The resulting `llama-server` is an arm64 Mach-O binary with `libggml-metal` linked. The Mac's existing newer build (`b29c606e2`) was not used.

The exact build is therefore technically usable on Apple Silicon/Metal at the build level. No model load or inference smoke test was performed because the model and resource gates were not satisfied.

## Mac preflight evidence

- Host: Mac Studio `Mac13,1`, Apple M1 Max, 24-core GPU
- OS: macOS `26.6.2` / Darwin `25.6.0`
- Unified memory: 32 GiB
- Metal: Metal 4
- Current system-wide memory free percentage: 86% at the final read-only snapshot
- Current encrypted swap: 8 GiB total, approximately 6.92 GiB used
- Current background usage: several Chrome/Go/system processes; the largest sampled RSS values were approximately 0.75 GiB, 0.63 GiB, 0.43 GiB, and 0.42 GiB
- Model loaded: no
- Context/slot configuration: not started; intended bridge configuration remains one slot and 16,384 tokens
- Generation configuration: not started; intended frozen Qwen3 configuration remains temperature 0, seed 0, max 768, thinking disabled

The existing swap state was not cleared, swap settings were not changed, caches were not dropped, and unrelated processes were not killed. The Mac therefore cannot be certified as a clean bridge baseline in this state.

## Model identity gate

The historical runner identifies the required artifact as:

`Qwen_Qwen3-4B-Q4_K_M.gguf`

The exact file was not found in the workspace, `<WORKDIR>/`, or the local user tree. The ThinkPad endpoint, which historically held `<HOME>/research-inference/models/mm-agent/Qwen_Qwen3-4B-Q4_K_M.gguf`, was unreachable by SSH at audit time, so its SHA-256 could not be retrieved. No replacement download, alternate quantization, or unverified artifact was used.

Because exact model identity is a frozen comparison requirement, the bridge is stopped rather than run with an unverified Qwen3 4B file.

## Required conditions to resume

Resume only after both conditions are satisfied:

1. Retrieve and record the SHA-256 of the exact historical Qwen3 4B Q4_K_M GGUF, then place that unchanged artifact under a separately recorded Mac bridge model path.
2. Establish a naturally clean Mac baseline under the existing host state. Do not manually clear swap or alter memory settings to manufacture eligibility; if the frozen resource protocol cannot distinguish the pre-existing swap baseline, stop again.

After those checks, the only authorized execution is one complete `QWEN3-4B-MAC-METAL-BRIDGE-R1`, Q01–Q07, using the exact built commit, one slot, 16,384 context, unchanged V2 tasks/prompts/scorer/simulator, and frozen generation settings. No 8B model may start before that bridge is reviewed.

