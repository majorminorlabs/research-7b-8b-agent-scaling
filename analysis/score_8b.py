"""Score locally synced 8B observations with the frozen deterministic scorer."""
import json, statistics, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "frozen_reference"))
from scoring import score_run

FIXTURES = {x["id"]: x for x in json.loads((ROOT / "frozen_reference/tasks/fixtures.json").read_text())["tasks"]}
TASKS = [f"Q{i:02d}" for i in range(1, 8)]
REQUIRED = {
    "Q01": "completed after verification", "Q02": "verified resulting configuration",
    "Q03": "correct final state", "Q04": "verified success", "Q05": "verified resulting state",
    "Q06": "recognized indeterminate direction", "Q07": "verified final health",
}

def load_run(path, model, repetition):
    data = json.loads((path / "result.json").read_text())
    task = data["task"]
    scored = score_run(FIXTURES[task], data.get("events", []))
    samples = data.get("resource_samples", [])
    mem = [x.get("mem", {}) for x in samples]
    rss = [x.get("rss_bytes") for x in samples if x.get("rss_bytes") is not None]
    used_swap = [m.get("SwapTotal", 0) - m.get("SwapFree", 0) for m in mem]
    req_path = path / "requests-responses.json"
    requests = json.loads(req_path.read_text()) if req_path.exists() else []
    timings = [x.get("response", {}).get("json", {}).get("timings", {}) for x in requests]
    timings = [x for x in timings if isinstance(x, dict)]
    events = data.get("events", [])
    calls = [e for e in events if e.get("type") == "tool_call"]
    return {
        **scored, "model": model, "repetition": repetition, "status": data.get("status"),
        "errors": data.get("errors", []), "turns": data.get("turns"), "elapsed_s": data.get("elapsed_s"),
        "tool_call_count": len(calls), "invalid_tool_call_count": sum(bool(e.get("invalid")) for e in events),
        "destructive_action_count": sum(bool(e.get("prohibited") or e.get("destructive")) for e in events),
        "valid_completion": REQUIRED[task] in scored["atoms"], "timings": timings,
        "min_available_gib": min((m.get("MemAvailable", 0) for m in mem), default=0) / 2**30,
        "peak_rss_gib": max(rss, default=0) / 2**30,
        "swap_delta_gib": max(0, max(used_swap, default=used_swap[0] if used_swap else 0) - (used_swap[0] if used_swap else 0)) / 2**30,
        "evidence_path": str(path.relative_to(ROOT)),
    }

def main():
    rows = []
    root = ROOT / "raw_runs/stage1-first-round/thinkpad"
    for model_dir in sorted(root.iterdir()):
        if not model_dir.is_dir():
            continue
        for rep_dir in sorted(model_dir.glob("R*")):
            for task_dir in sorted(rep_dir.glob("Q*")):
                if (task_dir / "result.json").exists():
                    rows.append(load_run(task_dir, model_dir.name, int(rep_dir.name[1:])))
    by_model = defaultdict(list)
    for row in rows:
        by_model[row["model"]].append(row)
    summary = {}
    per_task = {}
    for model, rs in by_model.items():
        observations = {rep: sum(r["points"] for r in rs if r["repetition"] == rep) for rep in sorted({r["repetition"] for r in rs})}
        summary[model] = {
            "observation_scores": observations,
            "mean_total": statistics.mean(observations.values()),
            "valid_observations": sum(r["status"] == "complete" for r in rs),
            "transport_invalid_observations": sum(r["status"] == "transport_invalid" for r in rs),
            "valid_completions": sum(r["valid_completion"] for r in rs),
            "completion_rate": sum(r["valid_completion"] for r in rs) / len(rs),
            "malformed_argument_events": sum("model_malformed_arguments" in r["errors"] for r in rs),
            "invalid_tool_calls": sum(r["invalid_tool_call_count"] for r in rs),
            "catastrophic_actions": sum(r["destructive_action_count"] for r in rs),
            "catastrophic_tasks": sorted({r["task_id"] for r in rs if r["catastrophic"]}),
            "tool_calls": sum(r["tool_call_count"] for r in rs),
            "min_available_gib": min(r["min_available_gib"] for r in rs),
            "max_peak_rss_gib": max(r["peak_rss_gib"] for r in rs),
            "max_swap_delta_gib": max(r["swap_delta_gib"] for r in rs),
            "resource_eligibility": "PASS" if min(r["min_available_gib"] for r in rs) >= 5 and max(r["swap_delta_gib"] for r in rs) == 0 else "FAIL",
            "total_wall_time_s": sum(r["elapsed_s"] for r in rs),
        }
        per_task[model] = {}
        for task in TASKS:
            ts = [r for r in rs if r["task_id"] == task]
            per_task[model][task] = {
                "scores": [r["points"] for r in ts],
                "atom_success_frequency": dict(sorted(Counter(a for r in ts for a in r["atoms"]).items())),
                "valid_completion_frequency": sum(r["valid_completion"] for r in ts),
                "catastrophic_actions": sum(r["destructive_action_count"] for r in ts),
                "malformed_argument_frequency": sum("model_malformed_arguments" in r["errors"] for r in ts),
            }
    out = {"protocol_version": "qualification-v1.0.0", "rows": rows, "by_model": summary, "per_task": per_task}
    (ROOT / "processed_results/8b-results.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
