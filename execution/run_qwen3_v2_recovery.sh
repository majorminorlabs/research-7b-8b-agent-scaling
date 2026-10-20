#!/usr/bin/env bash
set -euo pipefail

ROOT=<HOME>/research-inference/mm-8b-benchmark
MODEL=<HOME>/research-inference/models/mm-8b-scaling/Qwen3-8B-Q4_K_M.gguf
SERVER=<HOME>/research-inference/build-vulkan/bin/llama-server
FIXTURE="$ROOT/frozen_reference/tasks/fixtures.json"
OUT="$ROOT/raw_runs/stage1-v2-recovery/thinkpad/Qwen3-8B/R1-recovery-context16384-1slot"
LOG="$ROOT/logs/server/qwen3-v2-recovery-context16384-1slot.log"
PIDFILE="$ROOT/logs/server/qwen3-v2-recovery-context16384-1slot.pid"
PREFLIGHT="$ROOT/logs/server/qwen3-v2-recovery-context16384-1slot-preflight.txt"
BASE=http://127.0.0.1:18088

mkdir -p "$OUT" "$(dirname "$LOG")"
{
  date
  hostname
  uname -a
  free -h
  swapon --show || true
  pgrep -af 'llama-(server|cli)' || true
  "$SERVER" --version 2>&1 | head -8
  sha256sum "$MODEL"
  printf 'launch: %q ' "$SERVER" -m "$MODEL" --host 127.0.0.1 --port 18088 -ngl 99 -c 16384 -n 768 --temp 0 --seed 0 --parallel 1
  echo
} > "$PREFLIGHT"

"$SERVER" -m "$MODEL" --host 127.0.0.1 --port 18088 -ngl 99 -c 16384 -n 768 --temp 0 --seed 0 --parallel 1 > "$LOG" 2>&1 &
SERVER_PID=$!
echo "$SERVER_PID" > "$PIDFILE"
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT

for _ in $(seq 1 120); do
  if curl -fsS "$BASE/health" >/dev/null 2>&1; then break; fi
  sleep 1
done
curl -fsS "$BASE/health" >/dev/null

for task in Q01 Q02 Q03 Q04 Q05 Q06 Q07; do
  task_out="$OUT/$task"
  mkdir -p "$task_out"
  python3 "$ROOT/execution/v2_replay.py" \
    --fixture "$FIXTURE" --model Qwen3-8B --task "$task" \
    --base "$BASE" --output "$task_out" --server-pid "$SERVER_PID" \
    --thinking-off > "$task_out/controller-stdout.json"
done

wait "$SERVER_PID" || true
