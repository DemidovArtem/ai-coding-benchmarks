"""Git footprint on immutable commits, using the benchmark's source/test filters."""

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def parse_numstat(data):
    fields = iter(data.split(b"\0"))
    rows = {}
    for field in fields:
        if not field:
            continue
        added, deleted, path = field.split(b"\t", 2)
        old, new = (next(fields), next(fields)) if not path else (path, path)
        rows[(old.decode(errors="surrogateescape"), new.decode(errors="surrogateescape"))] = (
            None if added == b"-" else int(added), None if deleted == b"-" else int(deleted))
    return rows


def production_content(content, path):
    from harness.utils.rust_test_filter import find_test_ranges_from_content, remove_test_regions
    text = content.decode("utf-8")
    ranges = find_test_ranges_from_content(text, path, only_root_level=False)
    return remove_test_regions(text, ranges)


def codex_usage(events):
    """Codex turn.completed counters are cumulative per thread, not per resume."""
    fields = ("input_tokens", "output_tokens", "cached_input_tokens", "reasoning_output_tokens")
    sessions, tools, anomalies = {}, {}, []
    thread = None
    turns = 0
    for event in events:
        if event.get("type") == "thread.started":
            thread = event.get("thread_id") or event.get("thread", {}).get("id")
        if event.get("type") == "item.completed":
            item = event.get("item", {})
            if item.get("type") in ("command_execution", "mcp_tool_call"):
                key = item.get("server", "shell") if item["type"] == "mcp_tool_call" else "shell"
                tools[key] = tools.get(key, 0) + 1
        if event.get("type") != "turn.completed":
            continue
        turns += 1
        if not thread:
            anomalies.append("usage_without_thread_id")
            continue
        usage = {key: event.get("usage", {}).get(key) for key in fields}
        if any(value is not None and (type(value) is not int or value < 0) for value in usage.values()):
            raise ValueError("Invalid Codex token counter")
        previous = sessions.get(thread, {})
        if any(previous.get(key) is not None and value is not None and value < previous[key]
               for key, value in usage.items()):
            anomalies.append("cumulative_counter_decreased:" + thread)
        sessions[thread] = usage
    totals = {key: sum(row[key] for row in sessions.values())
              if sessions and not anomalies and all(row[key] is not None for row in sessions.values()) else None
              for key in fields}
    return {**totals, "session_ids": list(sessions), "turns": turns, "tool_calls": tools,
            "anomalies": anomalies, "counter_semantics": "last cumulative totals per thread; fields as reported"}


def normalize_grader(raw):
    """Preserve upstream decisions and diagnostics; never infer success from missing data."""
    resolved = raw.get("resolved")
    if resolved is not None and type(resolved) is not bool:
        raise ValueError("Grader resolved must be boolean or null")
    failure = None
    if raw.get("error_message"):
        failure = "evaluation_failure"
    elif raw.get("agent_created_tag") is False:
        failure = "missing_submission_tag"
    return {"resolved": resolved, "grader_metrics": raw,
            "f2p": raw.get("tests_status", {}).get("FAIL_TO_PASS"),
            "p2p": raw.get("tests_status", {}).get("PASS_TO_PASS"),
            "n2p": raw.get("tests_status", {}).get("NONE_TO_PASS"),
            "failure_category": failure}


def footprint(repo, base, end, metadata):
    from harness.utils.src_filter import SrcFileFilter
    source = SrcFileFilter(src_dirs=metadata["repo_src_dirs"], test_dirs=metadata["test_dirs"],
                           exclude_patterns=metadata.get("exclude_patterns"),
                           generated_patterns=metadata.get("generated_patterns"))

    def is_production(path):
        return bool(path and path.endswith(".rs") and source.is_src_file(path)
                    and not source.is_generated_file(path) and "vendor" not in Path(path).parts
                    and "generated" not in Path(path).parts)

    base = git(repo, "rev-parse", "--verify", "--end-of-options", base + "^{commit}").decode().strip()
    end = git(repo, "rev-parse", "--verify", "--end-of-options", end + "^{commit}").decode().strip()
    rename_flag = "-M" + str(metadata.get("rename_threshold", 50)) + "%"
    options = ("--no-ext-diff", "--no-textconv", "--diff-algorithm=myers", rename_flag)
    raw = parse_numstat(git(repo, "diff", *options, "--numstat", "-z", base, end, "--"))
    names = iter(git(repo, "diff", *options, "--name-status", "-z", base, end, "--").split(b"\0"))
    changes = []
    for status in names:
        if not status:
            continue
        first = next(names).decode(errors="surrogateescape")
        old, new = (first, next(names).decode(errors="surrogateescape")) if status.startswith(b"R") else (first, first)
        changes.append((status.decode(), None if status == b"A" else old, None if status == b"D" else new, raw[(old, new)]))
    result = {"starting_commit": base, "ending_commit": end,
              "added_prod_loc": 0, "deleted_prod_loc": 0, "changed_prod_files": 0,
              "new_prod_files": 0, "deleted_prod_files": 0, "renamed_prod_files": 0,
              "binary_changes": [], "formatting_only_files": [], "files": [],
              "rules": {"extension": ".rs", "inline_tests": "removed by pinned upstream Rust AST filter",
                        "excluded": ["metadata tests/exclusions/generated", "vendor directory", "generated directory"],
                        "loc": "physical lines including comments and blank lines", "rename_detection": rename_flag}}
    with tempfile.TemporaryDirectory(prefix="footprint-") as tmp:
        before, after = Path(tmp) / "before.rs", Path(tmp) / "after.rs"
        for status, old, new, counts in changes:
            row = {"status": status, "old_path": old, "new_path": new,
                   "raw_added": counts[0], "raw_deleted": counts[1]}
            result["files"].append(row)
            old_prod, new_prod = is_production(old), is_production(new)
            if counts[0] is None:
                result["binary_changes"].append(new or old)
                row["production_metrics"] = "binary_excluded"
                continue
            if not old_prod and not new_prod:
                row["production_metrics"] = "excluded"
                continue
            old_text = production_content(git(repo, "show", base + ":" + old), old) if old_prod else ""
            new_text = production_content(git(repo, "show", end + ":" + new), new) if new_prod else ""
            before.write_text(old_text)
            after.write_text(new_text)
            diff = subprocess.run(["git", "diff", "--no-ext-diff", "--no-textconv", "--diff-algorithm=myers",
                                   "--no-index", "--numstat", "--", str(before), str(after)], capture_output=True)
            if diff.returncode not in (0, 1):
                raise RuntimeError("Git production diff failed")
            fields = diff.stdout.split(b"\t")
            added, deleted = (int(fields[0]), int(fields[1])) if diff.stdout else (0, 0)
            row.update(added_prod_loc=added, deleted_prod_loc=deleted)
            result["added_prod_loc"] += added
            result["deleted_prod_loc"] += deleted
            if added or deleted or (status.startswith("R") and (old_prod or new_prod)):
                result["changed_prod_files"] += 1
                result["new_prod_files"] += int(new_prod and not old_prod)
                result["deleted_prod_files"] += int(old_prod and not new_prod)
                result["renamed_prod_files"] += int(status.startswith("R") and old_prod and new_prod)
            if old_prod and new_prod and not status.startswith("R") and (counts[0] or counts[1]):
                whitespace = subprocess.run(["git", "-C", str(repo), "diff", *options, "-w", "--ignore-blank-lines",
                                             "--exit-code", base, end, "--", new], capture_output=True)
                if whitespace.returncode == 0:
                    result["formatting_only_files"].append(new)
                elif whitespace.returncode != 1:
                    raise RuntimeError("Git whitespace comparison failed")
    cumulative = 0
    for encoded in git(repo, "ls-tree", "-r", "--name-only", "-z", end).split(b"\0"):
        path = encoded.decode(errors="surrogateescape")
        if is_production(path):
            content = git(repo, "show", end + ":" + path)
            if b"\0" not in content:
                cumulative += len(production_content(content, path).splitlines())
    result.update(net_prod_loc=result["added_prod_loc"] - result["deleted_prod_loc"],
                  churn_prod_loc=result["added_prod_loc"] + result["deleted_prod_loc"],
                  cumulative_prod_loc=cumulative)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "vendor/SWE-Milestone"))
    result = footprint(args.repo, args.base, args.end, json.loads(args.metadata.read_text()))
    args.output.write_text(json.dumps(result, indent=2) + "\n")
