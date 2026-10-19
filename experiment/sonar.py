"""Collect a completed local Sonar analysis; no scanner, service or model is launched."""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from experiment.security import redact


METRICS = ("ncloc", "lines", "complexity", "cognitive_complexity", "duplicated_lines", "duplicated_lines_density",
           "code_smells", "sqale_index", "software_quality_maintainability_issues", "software_quality_maintainability_remediation_effort")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class SonarClient:
    def __init__(self, url, token):
        parsed = urlsplit(url)
        if parsed.scheme != "http" or parsed.hostname != "127.0.0.1" or parsed.username or parsed.password or parsed.path not in ("", "/") or parsed.query or parsed.fragment:
            raise ValueError("Sonar URL must be an HTTP endpoint on 127.0.0.1 without credentials or a path")
        if not token or any(not 33 <= ord(char) <= 126 for char in token):
            raise ValueError("A nonempty Sonar token is required")
        self.url, self.token = url.rstrip("/"), token
        self.opener = build_opener(ProxyHandler({}), NoRedirect())

    def get(self, path, **params):
        if not path.startswith("/api/") or "?" in path or "#" in path:
            raise ValueError("Invalid Sonar API path")
        request = Request(self.url + path + "?" + urlencode(params), headers={"Authorization": "Bearer " + self.token})
        try:
            with self.opener.open(request, timeout=15) as response:
                body = response.read(10_000_001)
        except HTTPError as error:
            raise RuntimeError(f"Sonar HTTP {error.code} at {path}") from None
        except (URLError, TimeoutError):
            raise RuntimeError("Local Sonar API is unavailable") from None
        if len(body) > 10_000_000:
            raise ValueError("Sonar API response exceeds the collection budget")
        return body.decode().strip() if path == "/api/server/version" else json.loads(body)


def project_key(trial_id, snapshot_sha256):
    if not re.fullmatch(r"[0-9a-f]{64}", snapshot_sha256):
        raise ValueError("A real snapshot SHA-256 is required")
    identity = hashlib.sha256((trial_id + "\0" + snapshot_sha256).encode()).hexdigest()
    return "coding-experiment-" + identity[:40]


def normalize_measures(payload):
    values = {key: None for key in METRICS}
    for measure in payload.get("component", {}).get("measures", []):
        key = measure.get("metric")
        if key in values and "value" in measure:
            number = float(measure["value"])
            if not math.isfinite(number):
                raise ValueError("Sonar metric is not finite")
            values[key] = int(number) if number.is_integer() else number
    return values


def collect(client, task_id, expected_project, directory, expected_server_version, timeout=600):
    """The caller must bind expected_project to the snapshot at scanner launch."""
    directory.mkdir(parents=True, exist_ok=False)
    raw = {}
    result = {"analysis_ok": False, "new_maintainability_issues": None,
              "project_key": expected_project, "task_id": task_id, "metrics": {key: None for key in METRICS},
              "missing_metrics": list(METRICS), "failure_category": None, "server_version": None,
              "snapshot_sha256": None, "scanner_version": None, "source_exclusions": None,
              "snapshot_binding_verified": False, "rust_coverage_verified": False, "new_code_comparison_valid": False}
    started = time.monotonic()
    try:
        raw["server_version"] = client.get("/api/server/version")
        result["server_version"] = raw["server_version"]
        if raw["server_version"] != expected_server_version:
            raise ValueError("Sonar server version differs from the exact pin")
        deadline = started + timeout
        while True:
            raw["task"] = client.get("/api/ce/task", id=task_id)
            task = raw["task"]["task"]
            if task.get("id") != task_id or task.get("componentKey") != expected_project:
                raise ValueError("Sonar task identity differs from the submitted snapshot project")
            status = task.get("status")
            if status == "SUCCESS":
                break
            if status in ("FAILED", "CANCELED"):
                raise RuntimeError("Sonar background task " + status)
            if status not in ("PENDING", "IN_PROGRESS"):
                raise ValueError("Unknown Sonar background task status")
            if time.monotonic() >= deadline:
                raise TimeoutError("Sonar background task timeout")
            time.sleep(min(1, max(0, deadline - time.monotonic())))
        analysis_id = task.get("analysisId")
        if not analysis_id:
            raise ValueError("Completed Sonar task has no analysis ID")
        raw["analysis_before"] = client.get("/api/project_analyses/search", project=expected_project, ps=1)
        if not raw["analysis_before"].get("analyses") or raw["analysis_before"]["analyses"][0].get("key") != analysis_id:
            raise ValueError("Project has another latest analysis; refusing to misattribute metrics")
        available = set()
        raw["metric_catalog"] = []
        for page in range(1, 21):
            payload = client.get("/api/metrics/search", p=page, ps=500)
            raw["metric_catalog"].append(payload)
            available.update(row["key"] for row in payload["metrics"])
            if page * 500 >= payload["paging"]["total"]:
                break
        else:
            raise ValueError("Sonar metrics catalog exceeds the collection budget")
        requested = [key for key in METRICS if key in available]
        if not requested:
            raise ValueError("None of the required Sonar metrics is available")
        raw["measures"] = client.get("/api/measures/component", component=expected_project, metricKeys=",".join(requested))
        if raw["measures"].get("component", {}).get("key") != expected_project:
            raise ValueError("Sonar measures belong to another project")
        raw["quality_profiles"] = client.get("/api/qualityprofiles/search", project=expected_project)
        raw["plugins"] = client.get("/api/plugins/installed")
        if not any(profile.get("language") == "rust" for profile in raw["quality_profiles"].get("profiles", [])):
            raise ValueError("Rust quality profile is missing; Rust coverage is unverified")
        raw["analysis_after"] = client.get("/api/project_analyses/search", project=expected_project, ps=1)
        if raw["analysis_after"].get("analyses", [{}])[0].get("key") != analysis_id:
            raise ValueError("Project analysis changed during collection")
        metrics = normalize_measures(raw["measures"])
        if metrics["ncloc"] is None:
            raise ValueError("Rust source LOC is missing; analyzer coverage is unverified")
        result.update(analysis_ok=True, analysis_id=analysis_id, metrics=metrics,
                      missing_metrics=[key for key, value in metrics.items() if value is None])
    except (OSError, ValueError, RuntimeError, KeyError, TypeError, IndexError) as error:
        result.update(failure_category="sonar_analysis_failure", error=redact(str(error), {client.token}))
    finally:
        result["duration_seconds"] = time.monotonic() - started
        (directory / "raw.json").write_text(redact(json.dumps(raw, indent=2), {client.token}) + "\n")
        serialized = redact(json.dumps(result, indent=2), {client.token})
        (directory / "sonar.json").write_text(serialized + "\n")
        result = json.loads(serialized)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", default="http://127.0.0.1:9000")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--project-key", required=True)
    parser.add_argument("--server-version", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    client = SonarClient(args.server, os.environ.get("SONAR_TOKEN"))
    result = collect(client, args.task_id, args.project_key, args.output, args.server_version)
    print(json.dumps({"analysis_ok": result["analysis_ok"], "failure_category": result["failure_category"]}))
    raise SystemExit(0 if result["analysis_ok"] else 2)
