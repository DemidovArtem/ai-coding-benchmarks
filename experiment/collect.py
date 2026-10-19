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
    if sidecar.get("ok") is not True:
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



def sonar_result(run, record, common_base):
    directory = run / "sonar"
    sonar = load(directory / "sonar.json")
    if sonar is None:
        return record["sonar"]
    sonar = {**sonar, "artifacts_path":str(directory)}
    if sonar.get("analysis_ok") is not True:
        return sonar
    try:
        binding = load(directory / "binding.json", {})
        if not sonar.get("snapshot_binding_verified") or not sonar.get("rust_coverage_verified"):
            raise ValueError("Sonar snapshot binding or Rust coverage is unverified")
        if (sonar.get("snapshot_sha256") != record["snapshot_sha256"] or
                binding.get("snapshot_sha256") != record["snapshot_sha256"] or
                binding.get("submission_commit") != record["ending_commit"] or
                binding.get("kind") != "solution" or binding.get("trial_id") != run.name or
                binding.get("project_key") != sonar.get("project_key") or
                binding.get("protocol_sha256") != sonar.get("protocol_sha256")):
            raise ValueError("Sonar analysis does not belong to this graded submission")
        components = load(directory / "components.json", [])
        actual = {row["path"] for row in components if row.get("language") == "rust"}
        if not actual or actual != set(binding["source_files"]):
            raise ValueError("Sonar file coverage differs from the source binding")
        sonar["comparison_limitations"] = ["Raw snapshots include different inline test code; aggregate deltas are not production-only quality effects."]
        base = load(common_base / "sonar.json", {})
        base_binding = load(common_base / "binding.json", {})
        comparable = (base.get("analysis_ok") is True and base.get("snapshot_binding_verified") is True and
            base.get("rust_coverage_verified") is True and base_binding.get("kind") == "base" and
            base_binding.get("starting_tree") == record.get("starting_tree") and
            base.get("protocol_sha256") == sonar.get("protocol_sha256") and
            base.get("source_exclusions") == sonar.get("source_exclusions"))
        sonar["common_base_comparison_verified"] = comparable
        sonar["delta_vs_common_base"] = None
        if comparable:
            sonar["common_base_artifacts_path"] = str(common_base)
            sonar["delta_vs_common_base"] = {key:value-base["metrics"][key]
                if value is not None and base.get("metrics",{}).get(key) is not None else None
                for key,value in sonar["metrics"].items()}
    except (ValueError,KeyError,TypeError) as error:
        sonar.update(analysis_ok=False,failure_category="sonar_binding_failure",error=str(error))
        sonar["metrics"] = None
    return sonar


def collect(run, config):
    metadata = load(run / "run_metadata.json", {})
    config = load(run / "experiment.json", config)
    if metadata.get("state") not in ("finished", "failed"):
        raise ValueError("Trial is not terminal; do not collect a live run")
    raw = load(run / "evaluation/evaluation_result.json", {})
    proof = load(run / "effective_profile.json", {})
    sidecar = load(run / "evaluation/source_snapshot.integrity.json", {})
    record = {"experiment_id": config["experiment_id"], "trial_id": run.name,
              "trial_kind": metadata.get("trial_kind", "smoke"), "measured_comparison": metadata.get("measured_comparison", False),
              "variant": metadata.get("variant", "baseline"), "repo": config["benchmark"]["repo"],
              "milestone_id": config["benchmark"]["smoke_milestone"], "repetition": 1,
              "dataset_version": config["benchmark"]["version"], "dataset_commit": config["pins"]["git_commits"]["results/setup/dataset"],
              "model": metadata.get("model"), "reasoning_effort": metadata.get("reasoning_effort"),
              "starting_commit": proof.get("starting_commit"), "ending_commit": sidecar.get("agent_tag_commit"),
              "starting_tree": None, "effective_profile": proof,
              "duration_seconds": metadata.get("duration_seconds"),
              "sonar": {"analysis_ok": None, "new_maintainability_issues": None, "status": "not_run"},
              "quota": {"before": load(run / "quota_before.json", load(ROOT / "reports/quota_before_baseline_smoke.json")),
                        "after": load(run / "quota_after.json", load(ROOT / "reports/quota_after_baseline_smoke.json"))},
              "artifacts_path": str(run), "snapshot_sha256": sidecar.get("snapshot_sha256"),
              "capture_diagnostics": {key: sidecar.get(key) for key in (
                  "uncommitted_lost_count", "uncommitted_lost_sample", "uncommitted_outside_count", "committed_outside_count")},
              "implementation_commit": metadata.get("implementation_commit"),
              "trial_state":metadata.get("state"), "trial_failure_category":metadata.get("failure_category"),
              "skill_state":load(run / "serena_state.json"),
              "hook_activation_audit":load(run / "skill_activation.json"),
              "resume": metadata.get("resume"), "wall_duration_seconds":metadata.get("wall_duration_seconds"),
              "interruptions": [load(path) for path in sorted((run / "interruptions").glob("*/run_metadata.json"))],
              "collection_errors": [], **normalize_grader(raw)}
    record.update({key: None for key in ("added_prod_loc", "deleted_prod_loc", "net_prod_loc", "churn_prod_loc",
                                         "changed_prod_files", "cumulative_prod_loc")})
    if not raw:
        record["failure_category"] = metadata.get("failure_category", "missing_grader_result")
    elif metadata.get("state") == "failed":
        record["failure_category"] = record["failure_category"] or metadata.get("failure_category")
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
    planner_audit = load(run / "planner/audit.json", {})
    if record["variant"] in ("plan", "goal_plan"):
        planner_stdout = run / "planner/log/agent_stdout.txt"
        planner_events = [json.loads(line) for line in planner_stdout.read_text().splitlines() if line.startswith("{")] if planner_stdout.exists() else []
        record["usage"]["planner"] = {"used": True, **codex_usage(planner_events)}
        record["preparation"] = planner_audit
        record["session_isolation"] = load(run / "session_isolation.json")
    record["usage"]["total"] = {key: sum(record["usage"][phase][key] for phase in ("planner", "executor"))
        if all(record["usage"][phase].get(key) is not None for phase in ("planner", "executor")) else None
        for key in ("input_tokens", "output_tokens", "cached_input_tokens")}
    stats = load(run / "agent_stats.json", {}).get("summary", {})
    record["native_usage_observations"] = {key: stats.get(key) for key in ("total_turns", "total_tool_calls", "wall_clock_ms")}
    record["durations_seconds"] = {"planner": planner_audit.get("duration_seconds", 0 if record["variant"] not in ("plan", "goal_plan") else None), "executor": stats["wall_clock_ms"] / 1000 if stats.get("wall_clock_ms") is not None else None,
                                    "evaluation": load(run / "durations.json", {}).get("evaluation"), "sonar": None}
    setup = {key: config[key] for key in ("codex", "benchmark", "pins")}
    record["setup_fingerprint"] = metadata.get("setup_fingerprint") or hashlib.sha256(json.dumps(setup, sort_keys=True).encode()).hexdigest()
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
    record["sonar"] = sonar_result(run, record, ROOT / "results/sonar/common_base")
    record["durations_seconds"]["sonar"] = record["sonar"].get("duration_seconds")
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT / "vendor/SWE-Milestone"))
    records = [collect(run.resolve(), load(ROOT / "experiment.yaml")) for run in args.run]
    export(records, args.output)
    print(json.dumps([{key: record.get(key) for key in ("trial_id", "resolved", "added_prod_loc", "deleted_prod_loc", "failure_category", "collection_errors")} for record in records]))
