"""Score one preserved future V2 repetition without replaying the model."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scoring.v2.core import score_run

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "raw_runs/stage1-v2-recovery/thinkpad/Qwen3-8B/R1-recovery-context16384-1slot"
FIXTURES = {x["id"]: x for x in json.loads((ROOT / "frozen_reference/tasks/fixtures.json").read_text())["tasks"]}
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
    scored = score_run(FIXTURES[task], result.get("events", []), final_text)
    rows.append({"task": task, "status": result.get("status"), "points": scored["points"],
                 "max_points": scored["max_points"], "atoms": scored["atoms"],
                 "prohibited": scored["prohibited"], "final_plan_safe": scored["final_plan_safe"],
                 "turns": result.get("turns"), "elapsed_s": result.get("elapsed_s"),
                 "errors": result.get("errors", []), "evidence_path": str(path.relative_to(ROOT))})
out = {"model": "Qwen3-8B", "repetition": "R1-recovery-context16384-1slot",
       "benchmark_task_version": "v2.0.0", "scorer_version": "v2.0.0",
       "rows": rows, "total_points": sum(x["points"] for x in rows),
       "max_points": 80, "full_task_objectives": sum(bool(x["atoms"]) and x["points"] == x["max_points"] for x in rows)}
(ROOT / "processed_results/qwen3-v2-recovery-v2.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
print(json.dumps(out, indent=2, sort_keys=True))
