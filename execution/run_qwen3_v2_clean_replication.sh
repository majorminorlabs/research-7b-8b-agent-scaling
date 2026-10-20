#!/usr/bin/env bash
set -euo pipefail

ROOT=<HOME>/research-inference/mm-8b-benchmark
MODEL=<HOME>/research-inference/models/mm-8b-scaling/Qwen3-8B-Q4_K_M.gguf
SERVER=<HOME>/research-inference/build-vulkan/bin/llama-server
FIXTURE="$ROOT/frozen_reference/tasks/fixtures.json"
ID=R2-clean-replication-postreboot
OUT="$ROOT/raw_runs/stage1-v2-replication/thinkpad/Qwen3-8B/$ID"
LOGDIR="$ROOT/logs/server/$ID"
PORT=18089
BASE="http://127.0.0.1:$PORT"
PIDFILE="$LOGDIR/server.pid"
STOPFILE="$LOGDIR/telemetry.stop"
TELEMETRY="$LOGDIR/resource-telemetry.jsonl"
SERVERLOG="$LOGDIR/server.log"

mkdir -p "$OUT" "$LOGDIR"
rm -f "$PIDFILE" "$STOPFILE" "$TELEMETRY"

{
  date; hostname; uptime; cat /proc/uptime
  free -h; cat /proc/meminfo; cat /proc/sys/vm/swappiness; cat /proc/swaps
  cat /proc/pressure/memory 2>/dev/null || true; cat /proc/pressure/io 2>/dev/null || true
  ps -eo pid,ppid,rss,vsz,stat,comm,args --sort=-rss | head -40
  pgrep -af 'llama-(server|cli)' || true
  "$SERVER" --version 2>&1 | head -8
  stat -c '%n|%s|%b' "$MODEL"; sha256sum "$MODEL"
  vulkaninfo --summary 2>&1 | grep -E 'GPU[0-9]:|deviceName|deviceType|driverName|driverInfo|apiVersion' || true
  echo "launch=$SERVER -m $MODEL --host 127.0.0.1 --port $PORT -ngl 99 -c 16384 -n 768 --temp 0 --seed 0 --parallel 1"
} > "$LOGDIR/preflight-before-load.txt"

python3 "$ROOT/execution/resource_telemetry.py" --pidfile "$PIDFILE" --output "$TELEMETRY" --stopfile "$STOPFILE" --interval 1 > "$LOGDIR/telemetry-controller.log" 2>&1 &
TELEMETRY_PID=$!
"$SERVER" -m "$MODEL" --host 127.0.0.1 --port "$PORT" -ngl 99 -c 16384 -n 768 --temp 0 --seed 0 --parallel 1 > "$SERVERLOG" 2>&1 &
SERVER_PID=$!
echo "$SERVER_PID" > "$PIDFILE"
cleanup() {
  kill "$SERVER_PID" 2>/dev/null || true
  touch "$STOPFILE"
  wait "$TELEMETRY_PID" 2>/dev/null || true
}
trap cleanup EXIT

for _ in $(seq 1 120); do
  if curl -fsS "$BASE/health" >/dev/null 2>&1; then break; fi
  sleep 1
done
curl -fsS "$BASE/health" >/dev/null
{
  date; free -h; cat /proc/meminfo; cat /proc/sys/vm/swappiness; cat /proc/swaps
  cat /proc/pressure/memory 2>/dev/null || true; cat /proc/pressure/io 2>/dev/null || true
  ps -o pid,ppid,rss,vsz,stat,comm,args -p "$SERVER_PID" || true
} > "$LOGDIR/post-load.txt"

for task in Q01 Q02 Q03 Q04 Q05 Q06 Q07; do
  task_out="$OUT/$task"
  mkdir -p "$task_out"
  python3 "$ROOT/execution/v2_replay.py" --fixture "$FIXTURE" --model Qwen3-8B --task "$task" \
    --base "$BASE" --output "$task_out" --server-pid "$SERVER_PID" --thinking-off > "$task_out/controller-stdout.json"
done
