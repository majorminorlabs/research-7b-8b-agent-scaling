"""Read-only host/process telemetry for one model run."""
import argparse
import json
import pathlib
import time

KEYS = {
    "MemTotal", "MemFree", "MemAvailable", "Buffers", "Cached", "SwapCached",
    "Active", "Inactive", "Active_anon", "Inactive_anon", "Active_file",
    "Inactive_file", "AnonPages", "Mapped", "Shmem", "Slab", "SReclaimable",
    "SUnreclaim", "PageTables", "CommitLimit", "Committed_AS", "SwapTotal",
    "SwapFree", "Zswap", "Zswapped", "CmaFree",
}

def meminfo():
    out = {}
    for line in pathlib.Path("/proc/meminfo").read_text().splitlines():
        key, _, rest = line.partition(":")
        if key in KEYS:
            out[key] = int(rest.strip().split()[0]) * 1024
    out["SwapUsed"] = out.get("SwapTotal", 0) - out.get("SwapFree", 0)
    return out

def psi(path):
    try:
        return pathlib.Path(path).read_text().strip()
    except OSError:
        return None

def proc(pid):
    if not pid:
        return None
    base = pathlib.Path(f"/proc/{pid}")
    try:
        fields = {}
        for line in (base / "status").read_text().splitlines():
            key, _, value = line.partition(":")
            if key in {"Name", "State", "VmSize", "VmRSS", "RssAnon", "RssFile", "RssShmem", "VmSwap", "Threads"}:
                fields[key] = value.strip()
        return {"pid": pid, **fields}
    except OSError:
        return None

def vmstat():
    out = {}
    try:
        for line in pathlib.Path("/proc/vmstat").read_text().splitlines():
            key, value = line.split()[:2]
            if key in {"pswpin", "pswpout", "pgscan_kswapd", "pgscan_direct", "pgsteal_kswapd", "pgsteal_direct", "oom_kill"}:
                out[key] = int(value)
    except OSError:
        pass
    return out

def gpu():
    result = {}
    for pattern in ("/sys/class/drm/card*/device/mem_info_vram_used", "/sys/class/drm/card*/device/mem_info_vram_total", "/sys/class/drm/card*/device/gpu_busy_percent"):
        for path in pathlib.Path("/").glob(pattern.lstrip("/")):
            try:
                result[str(path)] = path.read_text().strip()
            except OSError:
                pass
    return result

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pidfile", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--stopfile", required=True)
    ap.add_argument("--interval", type=float, default=1.0)
    args = ap.parse_args()
    out = pathlib.Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as handle:
        while not pathlib.Path(args.stopfile).exists():
            pid = None
            try:
                pid = int(pathlib.Path(args.pidfile).read_text().strip())
            except (OSError, ValueError):
                pass
            row = {"epoch": time.time(), "monotonic": time.monotonic(),
                   "pid": pid, "meminfo": meminfo(), "psi_memory": psi("/proc/pressure/memory"),
                   "psi_io": psi("/proc/pressure/io"), "vmstat": vmstat(),
                   "server_proc": proc(pid), "gpu": gpu()}
            handle.write(json.dumps(row, sort_keys=True) + "\n")
            handle.flush()
            time.sleep(args.interval)

if __name__ == "__main__":
    main()
