#!/bin/zsh
# Launch one Mac/Metal cohort with the actual child PID, then run Q01-Q07.
# Request and scoring semantics remain in mac_bridge_replay.py and frozen V2.
set -euo pipefail

if [[ $# -ne 3 ]]; then
  print -u2 "usage: $0 MODEL_PATH RUN_ROOT PORT"
  exit 2
fi

model_path="$1"
run_root="$2"
port="$3"
repo_root="${${(%):-%x}:A:h:h}"
server_bin="$repo_root/runtime/llama.cpp-972d2313b/build-metal-arm64/bin/llama-server"
mkdir -p "$run_root"

"$server_bin" --model "$model_path" --host 127.0.0.1 --port "$port" \
  --gpu-layers 99 --ctx-size 16384 --parallel 1 --jinja \
  --temperature 0 --seed 0 > "$run_root/server.log" 2>&1 &
server_pid=$!
print -r -- "$server_pid" > "$run_root/server.pid"
print -r -- "$(date -u +%Y-%m-%dT%H:%M:%SZ) pid=$server_pid" > "$run_root/server-launch.txt"
trap 'kill "$server_pid" 2>/dev/null || true' EXIT INT TERM

for i in {1..120}; do
  if curl -fsS "http://127.0.0.1:${port}/health" >/dev/null 2>&1; then
    break
  fi
  if ! kill -0 "$server_pid" 2>/dev/null; then
    print -u2 "llama-server exited before readiness"
    exit 1
  fi
  sleep 1
done

if ! curl -fsS "http://127.0.0.1:${port}/health" >/dev/null 2>&1; then
  print -u2 "llama-server readiness timeout"
  exit 1
fi

for task in Q01 Q02 Q03 Q04 Q05 Q06 Q07; do
  arch -arm64 python3 "$repo_root/execution/mac_bridge_replay.py" \
    --fixture "$repo_root/frozen_reference/tasks/fixtures.json" \
    --model "${MODEL_NAME:?MODEL_NAME must be set}" --task "$task" \
    --base "http://127.0.0.1:${port}" \
    --output "$run_root/$task" --server-pid "$server_pid" --thinking-off
done
