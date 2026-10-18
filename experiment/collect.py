"""Collect a completed baseline smoke without modifying or re-running its grader."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile

from experiment.metrics import codex_usage, footprint, git, normalize_grader
from experiment.report import export


ROOT = Path(__file__).resolve().parents[1]


def load(path, default=None):
    return json.loads(path.read_text()) if path.exists() else default


def verify_snapshot(snapshot, sidecar, repo):
    if hashlib.sha256(snapshot.read_bytes()).hexdigest() != sidecar.get("snapshot_sha256"):
        raise ValueError("Snapshot SHA-256 differs from capture sidecar")
    if sidecar.get("ok") is not True or sidecar.get("uncommitted_lost_count"):
        raise ValueError("Snapshot capture integrity is unverified")
    end = sidecar["agent_tag_commit"]
    actual = git(repo, "rev-parse", "--verify", "--end-of-options", sidecar["tag"] + "^{commit}").decode().strip()
    if actual != end:
        raise ValueError("Submission tag differs from captured commit")
    checked = 0
    with tarfile.open(snapshot) as archive:
        for member in archive.getmembers():
            path = member.name.removeprefix("./")
            if member.isfile() and path.endswith(".rs"):
                content = archive.extractfile(member).read()
                if content != git(repo, "show", end + ":" + path):
                    raise ValueError("Snapshot Rust content differs from submission commit: " + path)
                checked += 1
    if not checked:
        raise ValueError("Snapshot contains no verifiable Rust source")
    return checked


def collect(run, config):
    metadata = load(run / "run_metadata.json", {})
    if metadata.get("state") not in ("finished", "failed"):
        raise ValueError("Trial is not terminal; do not collect a live run")
    raw = load(run / "evaluation/evaluation_result.json", {})
    proof = load(run / "effective_profile.json", {})
    sidecar = load(run / "evaluation/source_snapshot.integrity.json", {})
    record = {"experiment_id": config["experiment_id"], "trial_id": run.name,
              "trial_kind": "smoke", "measured_comparison": False,
              "variant": "baseline", "repo": config["benchmark"]["repo"],
              "milestone_id": config["benchmark"]["smoke_milestone"], "repetition": 1,
              "dataset_version": config["benchmark"]["version"], "dataset_commit": config["pins"]["git_commits"]["results/setup/dataset"],
              "model": metadata.get("model"), "reasoning_effort": metadata.get("reasoning_effort"),
              "starting_commit": proof.get("starting_commit"), "ending_commit": sidecar.get("agent_tag_commit"),
              "starting_tree": None, "effective_profile": proof,
              "duration_seconds": metadata.get("duration_seconds"),
              "sonar": {"analysis_ok": None, "new_maintainability_issues": None, "status": "not_run"},
              "quota": {"before": load(ROOT / "reports/quota_before_baseline_smoke.json"),
                        "after": load(ROOT / "reports/quota_after_baseline_smoke.json")},
              "artifacts_path": str(run), "snapshot_sha256": sidecar.get("snapshot_sha256"),
              "implementation_commit": metadata.get("implementation_commit"),
              "collection_errors": [], **normalize_grader(raw)}
    record.update({key: None for key in ("added_prod_loc", "deleted_prod_loc", "net_prod_loc", "churn_prod_loc",
                                         "changed_prod_files", "cumulative_prod_loc")})
    if not raw:
        record["failure_category"] = metadata.get("failure_category", "missing_grader_result")
    stdout = run / "log/agent_stdout.txt"
    events = []
    if stdout.exists():
        for line in stdout.read_text().splitlines():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    record["usage"] = {"planner": {"used": False, "input_tokens": 0, "output_tokens": 0, "cached_input_tokens": 0},
                       "executor": codex_usage(events)}
    stats = load(run / "agent_stats.json", {}).get("summary", {})
    record["native_usage_observations"] = {key: stats.get(key) for key in ("total_turns", "total_tool_calls", "wall_clock_ms")}
    record["durations_seconds"] = {"planner": 0, "executor": stats["wall_clock_ms"] / 1000 if stats.get("wall_clock_ms") is not None else None,
                                    "evaluation": None, "sonar": None}
    setup = {key: config[key] for key in ("codex", "benchmark", "pins")}
    record["setup_fingerprint"] = hashlib.sha256(json.dumps(setup, sort_keys=True).encode()).hexdigest()
    if record["starting_commit"] and record["ending_commit"] and raw.get("agent_created_tag") is True:
        try:
            repo = run / "metrics_repository"
            if not repo.exists():
                subprocess.run(["git", "clone", "--quiet", str(run / "repository.bundle"), str(repo)], check=True, capture_output=True)
            checked = verify_snapshot(run / "evaluation/source_snapshot.tar", sidecar, repo)
            capture = sidecar["capture_filter"]
            filters = {"repo_src_dirs": capture["src_dirs"], **{key: capture[key] for key in ("test_dirs", "exclude_patterns", "generated_patterns")}}
            metrics = footprint(repo, record["starting_commit"], record["ending_commit"], filters)
            record.update(metrics)
            record["starting_tree"] = git(repo, "rev-parse", record["starting_commit"] + "^{tree}").decode().strip()
            record["verified_snapshot_rust_files"] = checked
        except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
            record["collection_errors"].append(str(error))
            record["failure_category"] = record["failure_category"] or "collection_failure"
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT / "vendor/SWE-Milestone"))
    record = collect(args.run.resolve(), load(ROOT / "experiment.yaml"))
    export([record], args.output)
    print(json.dumps({key: record.get(key) for key in ("trial_id", "resolved", "added_prod_loc", "deleted_prod_loc", "failure_category", "collection_errors")}))
