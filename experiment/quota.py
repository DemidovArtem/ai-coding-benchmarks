"""Read approximate account limits without starting a model turn."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import selectors
import subprocess
import time


def read_quota(timeout=20):
    report = _read_quota_once(timeout)
    if report['status'] == 'timeout':
        retry = _read_quota_once(timeout)
        retry['previous_observation'] = report
        return retry
    return report


def wait_for_quota(output, read=None, sleep=None, on_wait=None):
    """Keep the calling process alive at 2% or less remaining in the 300-minute window."""
    read, sleep = read or read_quota, sleep or time.sleep
    path = Path(output) / 'quota_wait.json'
    observations = []
    while True:
        snapshot = read()
        quotas = list((snapshot.get('rate_limits') or {}).values())
        windows = [q.get(key) for q in quotas for key in ('primary', 'secondary')]
        short = [w for w in windows if w and w.get('windowDurationMins') == 300]
        if snapshot.get('status') != 'observed' or not short:
            state = 'waiting_observation'
        elif any(q.get('spendControlReached') for q in quotas):
            raise RuntimeError('Account spend control prevents inference')
        elif any(w['usedPercent'] >= 100 for w in windows if w and w.get('windowDurationMins') != 300):
            raise RuntimeError('Long-window quota exhausted; preserve the session')
        elif any(w['usedPercent'] >= 98 for w in short):
            state = 'waiting_quota'
        elif any(q.get('rateLimitReachedType') for q in quotas):
            state = 'waiting_quota'
        else:
            path.write_text(json.dumps({'state': 'ready', 'observations': observations, 'current': snapshot}, indent=2) + '\n')
            return snapshot
        observations.append({'state': state, 'snapshot': snapshot})
        path.write_text(json.dumps({'state': state, 'observations': observations}, indent=2) + '\n')
        if on_wait:
            on_wait(state)
        sleep(60)


def _read_quota_once(timeout):
    report = {"observed_at": datetime.now(timezone.utc).isoformat(),
              "source": "codex app-server account/rateLimits/read", "approximate": True,
              "status": "timeout", "rate_limits": None}
    process = subprocess.Popen(["codex", "app-server", "--stdio"], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0)

    def send(value):
        process.stdin.write((json.dumps(value) + "\n").encode())
        process.stdin.flush()

    send({"id": 1, "method": "initialize", "params": {
        "clientInfo": {"name": "ai-coding-environment-audit", "version": "0.1.0"}}})
    pending = b""
    deadline = time.monotonic() + timeout
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    try:
        while time.monotonic() < deadline:
            if not selector.select(timeout=min(1, max(0, deadline - time.monotonic()))):
                continue
            chunk = os.read(process.stdout.fileno(), 65536)
            if not chunk:
                report["status"] = "process_ended"
                break
            pending += chunk
            while b"\n" in pending:
                line, pending = pending.split(b"\n", 1)
                event = json.loads(line)
                if event.get("id") == 1:
                    if "error" in event:
                        report["status"] = "initialization_failed"
                        return report
                    send({"method": "initialized"})
                    send({"id": 2, "method": "account/rateLimits/read", "params": None})
                if event.get("id") == 2:
                    if "result" in event:
                        result = event["result"]
                        limits = result.get("rateLimitsByLimitId") or {"default": result.get("rateLimits", {})}
                        report["rate_limits"] = {key: {
                            field: value.get(field) for field in
                            ("primary", "secondary", "rateLimitReachedType", "spendControlReached")
                        } for key, value in limits.items() if isinstance(value, dict)}
                        report["status"] = "observed"
                    else:
                        report["status"] = "request_failed"
                    return report
    finally:
        selector.close()
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        process.stdin.close()
        process.stdout.close()
    return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = read_quota()
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))
