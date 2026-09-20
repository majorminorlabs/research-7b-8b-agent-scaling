# Model and dependency notices

This package contains benchmark code, metadata, documentation, and canonical results. It does not contain model weights.

Model identities, pinned revisions, GGUF sources, hashes, and license/provenance notes are recorded in `manifests/` and `provenance/`. Public use must comply with each upstream model license:

- Qwen3: Apache-2.0; https://huggingface.co/Qwen/Qwen3-4B
- Qwen2.5: Qwen license as recorded by the upstream release; https://huggingface.co/Qwen/Qwen2.5-3B-Instruct
- Granite 4.1: Apache-2.0; https://huggingface.co/ibm-granite/granite-4.1-3b
- Ministral 3: Apache-2.0; https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512

llama.cpp is an external runtime pinned by commit and is not vendored. Source links and revision identities are provenance, not redistribution of upstream weights or license grants.
