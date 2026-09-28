#!/usr/bin/env python3
"""Read-only 3-minute status and model-metric snapshots for the resumed Basic run."""
import argparse
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
import subprocess
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1] / "runs/basic002_030_v263_v290_run01"


def read(path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def snapshot():
    status = read(ROOT / "status.json")
    result = {"time": datetime.now(timezone.utc).isoformat(timespec="seconds"), "queue": status}
    result["completed_in_original_29_problem_queue"] = sum(
        read(path).get("state") in {"completed", "completed_with_failed_lanes"}
        for path in (ROOT / "problems").glob("*/summary.json")
    )
    problem = ROOT / "problems" / status.get("problem_id", "unknown")
    result["problem"] = read(problem / "status.json")
    result["lanes"] = {
        str(path.relative_to(problem)): read(path)
        for path in sorted((problem / "02_r1_cycles/lanes").glob("*/*_r1_cycle_*/status.json"))
    }
    result["lane_failures"] = {
        path.parent.name: read(path)
        for path in sorted((problem / "02_r1_cycles/lanes").glob("*/failure.json"))
    }
    result["servers"] = {}
    for role, port in [("gemma", 8030), ("qwen", 8027)]:
        try:
            with urlopen(f"http://127.0.0.1:{port}/metrics", timeout=5) as response:
                metrics = response.read().decode()
            wanted = ("num_requests_running", "num_requests_waiting", "generation_tokens_total",
                      "prompt_tokens_total", "num_preemptions_total", "spec_decode_num_drafts_total",
                      "spec_decode_num_draft_tokens_total", "spec_decode_num_accepted_tokens_total")
            values = {}
            for line in metrics.splitlines():
                if any(line.startswith(f"vllm:{key}{{") for key in wanted):
                    key = line.split("{", 1)[0].removeprefix("vllm:")
                    values[key] = values.get(key, 0) + float(line.rsplit(" ", 1)[1])
            result["servers"][role] = values
        except Exception as error:
            result["servers"][role] = {"error": str(error)}
    try:
        result["gpus"] = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=index,memory.used,utilization.gpu", "--format=csv,noheader"],
            text=True, timeout=10,
        ).strip().splitlines()
    except Exception as error:
        result["gpu_error"] = str(error)
    return result


def main():
    global ROOT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--run-root", type=Path, default=ROOT)
    args = parser.parse_args()
    ROOT = args.run_root.resolve()
    with (ROOT / "monitor_mtp4.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        while True:
            row = snapshot()
            encoded = json.dumps(row, ensure_ascii=False)
            temporary = ROOT / "monitor_latest.json.tmp"
            temporary.write_text(json.dumps(row, indent=2) + "\n")
            temporary.replace(ROOT / "monitor_latest.json")
            with (ROOT / "monitor_3min.jsonl").open("a") as log:
                log.write(encoded + "\n")
            print(encoded, flush=True)
            if args.once or row["queue"].get("state") in {
                "completed", "completed_with_failed_lanes", "paused_on_failure", "stopped", "stopped_by_user", "failed_closed"
            }:
                return
            time.sleep(180)


if __name__ == "__main__":
    main()
