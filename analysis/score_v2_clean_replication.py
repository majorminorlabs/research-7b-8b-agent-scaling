"""Score and summarize the preserved post-reboot Qwen3 V2 replication."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scoring.v2.core import score_run

ID = "R2-clean-replication-postreboot"
BASE = ROOT / f"raw_runs/stage1-v2-replication/thinkpad/Qwen3-8B/{ID}"
LOG = ROOT / f"logs/server/{ID}"
fixtures = {x["id"]: x for x in json.loads((ROOT / "frozen_reference/tasks/fixtures.json").read_text())["tasks"]}
rows = []
for task in [f"Q{i:02d}" for i in range(1, 8)]:
    path = BASE / task
    result = json.loads((path / "result.json").read_text())
    requests = json.loads((path / "requests-responses.json").read_text())
    final_text = ""
    for item in reversed(requests):
        msg = ((item.get("response", {}).get("json", {}).get("choices") or [{}])[0].get("message") or {})
        if msg.get("content"):
            final_text = msg["content"]
            break
    scored = score_run(fixtures[task], result.get("events", []), final_text)
    rows.append({"task": task, "status": result.get("status"), "points": scored["points"],
                 "max_points": scored["max_points"], "atoms": scored["atoms"],
                 "prohibited": scored["prohibited"], "final_plan_safe": scored["final_plan_safe"],
                 "turns": result.get("turns"), "elapsed_s": result.get("elapsed_s"),
                 "errors": result.get("errors", []), "evidence_path": str(path.relative_to(ROOT))})

def parse_psi(text):
    out = {}
    if not text:
        return out
    for line in text.splitlines():
        fields = dict(re.findall(r"(avg10|avg60|avg300|total)=(\S+)", line))
        if line.startswith("some "): out["some"] = fields
        if line.startswith("full "): out["full"] = fields
    return out

telemetry = [json.loads(line) for line in (LOG / "resource-telemetry.jsonl").read_text().splitlines() if line.strip()]
mem = [x["meminfo"] for x in telemetry]
swap = [m["SwapUsed"] for m in mem]
rss = [int(x["server_proc"]["VmRSS"].split()[0]) * 1024 for x in telemetry if x.get("server_proc") and x["server_proc"].get("VmRSS")]
vsz = [int(x["server_proc"]["VmSize"].split()[0]) * 1024 for x in telemetry if x.get("server_proc") and x["server_proc"].get("VmSize")]
gpu_used = [int(v) for x in telemetry for k, v in x.get("gpu", {}).items() if k.endswith("mem_info_vram_used")]
gpu_total = [int(v) for x in telemetry for k, v in x.get("gpu", {}).items() if k.endswith("mem_info_vram_total")]
psi_memory = [parse_psi(x.get("psi_memory")) for x in telemetry]
psi_io = [parse_psi(x.get("psi_io")) for x in telemetry]
resource = {
    "telemetry_samples": len(telemetry),
    "baseline_swap_bytes": swap[0], "final_swap_bytes": swap[-1],
    "maximum_swap_bytes": max(swap), "swap_delta_bytes": max(swap) - swap[0],
    "minimum_mem_available_bytes": min(m["MemAvailable"] for m in mem),
    "peak_server_rss_bytes": max(rss), "peak_server_vmsize_bytes": max(vsz),
    "vulkan_vram_used_max_bytes": max(gpu_used) if gpu_used else None,
    "vulkan_vram_total_bytes": max(gpu_total) if gpu_total else None,
    "memory_psi": psi_memory, "io_psi": psi_io,
    "oom_kill_counter_start": telemetry[0]["vmstat"].get("oom_kill"),
    "oom_kill_counter_end": telemetry[-1]["vmstat"].get("oom_kill"),
}
out = {"model": "Qwen3-8B", "model_source": "Qwen/Qwen3-8B", "replication_id": ID,
       "benchmark_task_version": "v2.0.0", "scorer_version": "v2.0.0", "rows": rows,
       "total_points": sum(x["points"] for x in rows), "max_points": 80,
       "full_task_objectives": sum(x["points"] == x["max_points"] for x in rows),
       "resource": resource,
       "resource_eligibility": "FAIL" if resource["minimum_mem_available_bytes"] < 5 * 2**30 or resource["swap_delta_bytes"] > 0 else "PASS"}
(ROOT / "processed_results/qwen3-v2-clean-replication-v2.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
print(json.dumps(out, indent=2, sort_keys=True))
