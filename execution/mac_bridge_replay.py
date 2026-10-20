"""Mac/Metal collector for the single Qwen3 4B V2 bridge.

The request, simulator, and frozen generation contract are inherited from
execution.v2_replay.py.  Only resource sampling is platform-specific.
"""

import json
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "frozen_reference"))
sys.path.insert(0, str(ROOT))

from execution import frozen_replay  # noqa: E402
from scoring.v2.future_simulator import SimulatorV2  # noqa: E402
from scoring.v2.tool_schema import tool_defs_v2  # noqa: E402


def _run(*args):
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:
        return f"ERROR:{type(exc).__name__}:{exc}"


def _rss(pid):
    value = _run("ps", "-p", str(pid), "-o", "rss=")
    try:
        return int(value) * 1024
    except ValueError:
        return None


def server_command(pid):
    return _run("ps", "-p", str(pid), "-o", "command=")


def validate_server_pid(pid):
    """Reject a telemetry target unless it is the actual llama-server process."""
    command = server_command(pid)
    if "llama-server" not in command:
        raise RuntimeError(f"telemetry PID {pid} is not llama-server: {command}")
    return command


def _swap():
    raw = _run("sysctl", "-n", "vm.swapusage")
    values = {}
    for token in raw.replace("=", " ").split():
        if token in {"total", "used", "free"}:
            continue
    # Keep the unparsed native string authoritative; parsers can differ across
    # macOS releases and the raw telemetry is preserved in every sample.
    return {"raw": raw}


def mac_sample(pid, phase):
    return {
        "epoch": time.time(),
        "phase": phase,
        "pid": pid,
        "rss_bytes": _rss(pid),
        "platform": "macOS",
        "swapusage": _swap(),
        "memory_pressure": _run("memory_pressure"),
        "vm_stat": _run("vm_stat"),
        "physical_memory_bytes": _run("sysctl", "-n", "hw.memsize"),
        "process_snapshot": _run("ps", "-p", str(pid), "-o", "pid,ppid,rss,vsz,%cpu,%mem,command=") if pid else "",
    }


frozen_replay.Simulator = SimulatorV2
frozen_replay.tool_defs = tool_defs_v2
frozen_replay.sample = mac_sample


if __name__ == "__main__":
    server_pid = int(sys.argv[sys.argv.index("--server-pid") + 1])
    validate_server_pid(server_pid)
    frozen_replay.main()
    output = pathlib.Path(sys.argv[sys.argv.index("--output") + 1])
    marker = {
        "benchmark_task_version": "qualification-v1.0.0",
        "scorer_version": "v2.0.0",
        "simulator_version": "v2.0.0",
        "runner": "execution/mac_bridge_replay.py",
        "resource_sampler": "macOS memory_pressure/vm_stat/vm.swapusage/ps",
    }
    (output / "v2-version.json").write_text(json.dumps(marker, indent=2, sort_keys=True) + "\n")
