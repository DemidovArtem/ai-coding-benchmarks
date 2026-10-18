"""Read-only, quarantined preparation in a fresh container and Codex session."""

import hashlib
import json
from pathlib import Path
import subprocess
import time

from experiment.profiles import activate_profile


ROOT = Path(__file__).resolve().parents[1]
GOAL_FIELDS = ("acceptance_criteria", "constraints", "non_goals", "regression_invariants")
GOAL_INSTRUCTIONS = {
    "plan": 'Set "goal" to null. Provide only the common plan fields.',
    "goal_plan": 'Also provide "goal": acceptance_criteria, constraints, non_goals, and regression_invariants. '
                 'Restate requirements comprehensively; the goal must not be a solution or a hidden-test hint.',
}
READ_ONLY_PROBE = '''
import errno,json,pathlib
p=pathlib.Path('/testbed/.experiment-write-probe')
try:
 p.write_text('probe')
except OSError as error:
 assert error.errno==errno.EROFS, 'write rejected for a reason other than a read-only filesystem'
 print(json.dumps({'write_errno':error.errno,'read_only':True}))
else:
 p.unlink()
 raise RuntimeError('repository mount is writable')
'''


def schema():
    strings = {"type": "array", "items": {"type": "string"}}
    goal = {"type": "object", "additionalProperties": False,
            "properties": {key: strings for key in GOAL_FIELDS}, "required": list(GOAL_FIELDS)}
    properties = {"objective": {"type": "string"}, "steps": strings, "verification": strings, "risks": strings,
                  "goal": {"anyOf": [{"type": "null"}, goal]}}
    return {"type": "object", "additionalProperties": False, "properties": properties, "required": list(properties)}


def planner_prompt(task, variant):
    if variant not in GOAL_INSTRUCTIONS:
        raise ValueError("Unknown planner variant")
    return (ROOT / "prompts/planner.md").read_text().format(task=task, goal_instruction=GOAL_INSTRUCTIONS[variant])


def validate_handoff(raw, variant):
    if len(raw.encode()) > 12000:
        raise ValueError("Planner output exceeds the shared byte budget")

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate planner output key")
            result[key] = value
        return result

    value = json.loads(raw, object_pairs_hook=unique)
    if not isinstance(value, dict) or set(value) != set(schema()["required"]):
        raise ValueError("Planner output has unexpected fields")

    def text(item):
        return isinstance(item, str) and 0 < len(item.strip()) <= 1000 and "```" not in item

    def strings(items, required=False):
        return isinstance(items, list) and int(required) <= len(items) <= 12 and all(text(item) for item in items)

    if not text(value["objective"]) or not all(strings(value[key], key != "risks") for key in ("steps", "verification", "risks")):
        raise ValueError("Planner output violates the shared plan bounds")
    if variant == "plan" and value["goal"] is not None:
        raise ValueError("Plan-only output contains a goal")
    if variant == "goal_plan":
        goal = value["goal"]
        if not isinstance(goal, dict) or set(goal) != set(GOAL_FIELDS) or not all(strings(goal[key], True) for key in GOAL_FIELDS):
            raise ValueError("Structured goal is missing or invalid")
    if variant not in GOAL_INSTRUCTIONS:
        raise ValueError("Unknown planner variant")
    return value


def repository_fingerprint(root):
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        digest.update(path.relative_to(root).as_posix().encode() + b"\0")
        if path.is_symlink():
            digest.update(b"symlink:" + str(path.readlink()).encode())
        elif path.is_file():
            digest.update(b"file:" + hashlib.sha256(path.read_bytes()).digest())
        else:
            digest.update(b"directory")
    return digest.hexdigest()


def prepare(executor, task, config, output, variant):
    from harness.e2e.agent_runner import AgentRunner
    from harness.e2e.agents.codex import CodexFramework
    from harness.e2e.container_setup import ContainerSetup
    from harness.e2e.log_parser import get_parser

    started = time.monotonic()
    directory = output / "planner"
    directory.mkdir()
    (output / "original_task.txt").write_text(task)
    bundle = "/tmp/planner-input.bundle"
    subprocess.run(["docker", "exec", "-w", "/testbed", executor.container_name, "git", "-c", "safe.directory=/testbed",
                    "bundle", "create", bundle, "--all"], check=True, capture_output=True)
    subprocess.run(["docker", "cp", executor.container_name + ":" + bundle, str(directory / "input.bundle")], check=True, capture_output=True)
    repository = directory / "repository"
    subprocess.run(["git", "clone", "--quiet", str(directory / "input.bundle"), str(repository)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repository), "remote", "remove", "origin"], check=True, capture_output=True)
    before = repository_fingerprint(repository)
    (directory / "schema.json").write_text(json.dumps(schema(), indent=2) + "\n")
    prompt = planner_prompt(task, variant)
    setup = ContainerSetup(container_name=executor.container_name + "-planner", image_name=executor.image_name,
        agent_name="codex", agent_framework_name="codex", agent_version=config["codex"]["version"],
        repo_name=executor.repo_name, runtime_policy_binding=executor.runtime_policy_binding)

    class PlannerFramework(CodexFramework):
        def build_run_command(self, *args, **kwargs):
            return super().build_run_command(*args, **kwargs) + (
                " --output-schema /home/fakeroot/planner-schema.json --output-last-message /home/fakeroot/handoff.json")

        def get_container_env_vars(self):
            return super().get_container_env_vars() + ["-e", "GIT_OPTIONAL_LOCKS=0"]

    audit = {"variant": variant, "repository_before_sha256": before, "state": "initializing",
             "planner_prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "planner_input_bytes": len(prompt.encode())}
    try:
        setup.start_container(extra_mounts=["--mount", f"type=bind,src={repository.resolve()},dst=/testbed,readonly"])
        setup.lock_network()
        activate_profile(setup, directory, config, variant, repository_mount=repository)
        probe = setup.docker_exec(["python3", "-c", READ_ONLY_PROBE])
        audit["write_probe"] = json.loads(probe.stdout)
        subprocess.run(["docker", "cp", str(directory / "schema.json"), setup.container_name + ":/home/fakeroot/planner-schema.json"], check=True, capture_output=True)
        setup.prepare_agent_invocation()
        planner = AgentRunner(container_name=setup.container_name, model=config["codex"]["model"], agent_name="codex",
                              reasoning_effort=config["codex"]["reasoning_effort"], timeout_ms=config["planning"]["timeout_seconds"] * 1000,
                              log_dir=directory / "log")
        planner._framework = PlannerFramework(reasoning_effort=config["codex"]["reasoning_effort"])
        inference_started = time.monotonic()
        success, session = planner.run(prompt)
        audit["model_duration_seconds"] = time.monotonic() - inference_started
        audit["session_id"] = session
        get_parser("codex").extract_raw_logs(setup.container_name, directory / "log")
        if not success:
            audit["failure_category"] = "auth_failure" if planner._last_auth_error else (
                "quota_pressure" if planner._last_rate_limit else "preparation_failure")
            raise RuntimeError("Planner failed; executor must not start")
        subprocess.run(["docker", "cp", setup.container_name + ":/home/fakeroot/handoff.json", str(directory / "handoff.json")], check=True, capture_output=True)
        raw = (directory / "handoff.json").read_text()
        validate_handoff(raw, variant)
        audit.update(state="validated", handoff_sha256=hashlib.sha256(raw.encode()).hexdigest(), handoff_bytes=len(raw.encode()))
    except Exception:
        audit["state"] = "failed"
        raise
    finally:
        audit["repository_after_sha256"] = repository_fingerprint(repository)
        audit["repository_unchanged"] = audit["repository_after_sha256"] == before
        audit["duration_seconds"] = time.monotonic() - started
        (directory / "audit.json").write_text(json.dumps(audit, indent=2) + "\n")
        setup.cleanup()
    if not audit["repository_unchanged"]:
        raise RuntimeError("Planner mutated its supplied repository")
    if executor.container_setup.docker_exec_git("rev-parse", "HEAD").stdout.strip() != executor._snapshot_baseline_commit:
        raise RuntimeError("Executor repository changed during preparation")
    return task + "\n\n" + (ROOT / "prompts/executor.md").read_text().format(handoff=raw)
