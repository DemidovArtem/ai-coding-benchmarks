"""Analyze one verified Rust grader snapshot or its common base, outside the agent container."""

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import time

from experiment.collect import load, verify_snapshot
from experiment.metrics import git
from experiment.security import redact
from experiment.sonar import SonarClient, collect, project_key
from experiment.sonar_bootstrap import request, VERSION

ROOT = Path(__file__).resolve().parents[1]
EXCLUSIONS = ("**/tests/**", "**/benches/**", "**/examples/**", "**/vendor/**", "**/generated/**")


def extract(archive, destination):
    members = archive.getmembers()
    seen = set()
    for member in members:
        path = PurePosixPath(member.name)
        if path.is_absolute() or ".." in path.parts or not (member.isfile() or member.isdir()) or path in seen:
            raise ValueError("Unsafe or duplicate snapshot archive member")
        seen.add(path)
    archive.extractall(destination, members=members, filter="data")


def rust_manifest(directory):
    return {str(path.relative_to(directory)):hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(directory.rglob("*.rs")) if path.is_file()}


def prepare(run, output, kind):
    sidecar = load(run / "evaluation/source_snapshot.integrity.json")
    snapshot = run / "evaluation/source_snapshot.tar"
    repository = run / "metrics_repository"
    if not repository.exists():
        subprocess.run(["git","clone","--quiet",str(run / "repository.bundle"),str(repository)],check=True,capture_output=True)
    verify_snapshot(snapshot, sidecar, repository)
    base = load(run / "effective_profile.json")["starting_commit"]
    stage = output / "source"
    stage.mkdir()
    with tarfile.open(fileobj=io.BytesIO(git(repository,"archive",base,"--",".",":(exclude)HomebrewFormula"))) as archive:
        extract(archive,stage)
    # This pilot replays only the frozen ripgrep capture contract; reject silent generalization.
    capture = sidecar["capture_filter"]
    if capture["src_dirs"] != ["crates"] or sidecar["manifest_overlay"]["baseline_commit"] != base:
        raise ValueError("Unsupported snapshot source roots or manifest baseline")
    from harness.utils.src_filter import SrcFileFilter
    source_filter = SrcFileFilter(src_dirs=capture["src_dirs"],test_dirs=capture["test_dirs"],
        exclude_patterns=capture["exclude_patterns"],generated_patterns=capture["generated_patterns"])
    support = {str(path.relative_to(stage)):path.read_bytes() for path in (stage / "crates").rglob("*")
               if path.is_file() and path.suffix != ".rs" and not source_filter.is_src_file(str(path.relative_to(stage)))}
    if kind == "solution":
        shutil.rmtree(stage / "crates")
        with tarfile.open(snapshot) as archive:
            if any(not (m.name.removeprefix("./").startswith("crates/") or m.name in ("crates","Cargo.lock")) for m in archive.getmembers()):
                raise ValueError("Snapshot has unsupported paths outside the frozen source roots")
            extract(archive,stage)
        for path in sidecar["manifest_overlay"]["deletes"]:
            if path != "Cargo.lock":
                raise ValueError("Unsupported build manifest deletion")
            (stage / path).unlink(missing_ok=True)
    for path, content in support.items():
        target = stage / path
        if not target.exists():
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(content)
    manifest = {path:sha for path,sha in rust_manifest(stage / "crates").items()
                if source_filter.is_src_file("crates/" + path) and not source_filter.is_generated_file("crates/" + path)}
    manifest = {"crates/"+path:sha for path,sha in manifest.items()}
    if not manifest:
        raise ValueError("No Rust source selected")
    if kind == "solution":
        with tarfile.open(snapshot) as archive:
            captured = {m.name.removeprefix("./"):hashlib.sha256(archive.extractfile(m).read()).hexdigest()
                        for m in archive.getmembers() if m.isfile() and m.name.endswith(".rs")}
        if manifest != captured:
            raise ValueError("Staged Rust files differ from the exact grader snapshot")
    identity = sidecar["snapshot_sha256"] if kind == "solution" else hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
    proof = {"kind":kind,"trial_id":run.name,"snapshot_sha256":identity,"graded_snapshot_sha256":sidecar["snapshot_sha256"],
             "submission_commit":sidecar["agent_tag_commit"] if kind == "solution" else base,
             "starting_commit":base,"starting_tree":git(repository,"rev-parse",base+"^{tree}").decode().strip(),
             "source_files":manifest,"source_exclusions":list(EXCLUSIONS),
             "excluded_build_support_sha256":{path:hashlib.sha256(content).hexdigest() for path,content in support.items()},
             "capture_filter":capture,"build_support":"unchanged common-base files plus captured Cargo.lock overlay",
             "source_bytes":"exact captured Rust including any inline tests; separate from AST-filtered physical LOC"}
    return stage, proof


def verify_protocol(client, protocol):
    plugin = next(row for row in client.get("/api/plugins/installed")["plugins"] if row["key"] == "rust")
    if any(plugin[key] != protocol["rust_plugin"][key] for key in ("key","version","hash")):
        raise ValueError("Rust analyzer differs from the frozen protocol")
    payload = client.get("/api/rules/search",qprofile=protocol["profile"]["key"],activation="true",ps=500,f="actives")
    active = {key:[{field:row.get(field) for field in ("qProfile","inherit","severity","params","impacts")} for row in values]
              for key,values in payload["actives"].items()}
    if hashlib.sha256(json.dumps(active,sort_keys=True).encode()).hexdigest() != protocol["active_rules_sha256"]:
        raise ValueError("Active Rust rules differ from the frozen protocol")


def scan(run, output, credentials, kind):
    output.mkdir(parents=True,exist_ok=False)
    started = time.monotonic()
    report = {"analysis_ok":False,"failure_category":"sonar_analysis_failure","snapshot_binding_verified":False,
              "rust_coverage_verified":False,"metrics":None}
    private = load(credentials)
    pins = load(ROOT / "sonar/setup_candidates.json")
    token_name = token = None
    try:
        protocol_path = ROOT / "sonar/analysis_protocol.json"
        protocol = load(protocol_path)
        client = SonarClient("http://127.0.0.1:9000",private["token"])
        if client.get("/api/server/version") != protocol["server_version"]:
            raise ValueError("Server version differs from the frozen protocol")
        if list(EXCLUSIONS) != protocol["source_exclusions"] or pins["clippy"] != protocol["clippy"] or pins["scanner_version"] != protocol["scanner_version"]:
            raise ValueError("Source filters or Clippy image differ from the frozen protocol")
        verify_protocol(client,protocol)
        stage, proof = prepare(run,output,kind)
        proof["protocol_sha256"] = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
        key = project_key(run.name if kind == "solution" else "common-base",proof["snapshot_sha256"])
        proof.update(project_key=key,scanner_version=pins["scanner_version"],clippy_image_id=pins["clippy"]["image_id"])
        (output / "binding.json").write_text(json.dumps(proof,indent=2)+"\n")
        before = rust_manifest(stage)
        build = ["docker","run","--rm","--pull=never","--network","none","--user","1000:1000",
                 "--cap-drop=ALL","--security-opt=no-new-privileges:true","--memory=3g","--cpus=2","--pids-limit=256",
                 "--mount",f"type=bind,src={stage},dst=/workspace,readonly","--tmpfs","/tmp:rw,exec,size=2g,mode=1777",
                 "-w","/workspace","-e","CARGO_TARGET_DIR=/tmp/target", "--entrypoint","cargo",pins["clippy"]["image_id"],
                 "clippy","--offline","--locked","--workspace","--lib","--bins","--message-format=json","--","--cap-lints","warn"]
        if build[build.index("clippy"):] != protocol["clippy_arguments"]:
            raise ValueError("Clippy arguments differ from the frozen protocol")
        build_started = time.monotonic()
        result = subprocess.run(build,capture_output=True,text=True,timeout=600)
        (output / "clippy.jsonl").write_text(result.stdout)
        (output / "clippy.stderr.txt").write_text(result.stderr)
        proof.update(clippy_returncode=result.returncode,clippy_duration_seconds=time.monotonic()-build_started,
                     clippy_report_sha256=hashlib.sha256(result.stdout.encode()).hexdigest(),
                     clippy_arguments=build[build.index("clippy"):],clippy_lint_cap="warn; diagnostics retained, compile errors still fatal")
        (output / "binding.json").write_text(json.dumps(proof,indent=2)+"\n")
        if result.returncode:
            raise RuntimeError("Offline Clippy failed; refusing a partial maintainability comparison")
        existing = client.get("/api/projects/search",projects=key)["components"]
        if not existing:
            request(private["password"],"/api/projects/create",project=key,name=key,visibility="private")
        elif len(existing) != 1 or existing[0].get("visibility") != "private":
            raise ValueError("Snapshot project must remain private")
        token_name = key + "-scanner"
        token = request(private["password"],"/api/user_tokens/generate",name=token_name,type="PROJECT_ANALYSIS_TOKEN",projectKey=key)["token"]
        work = output / "scanner_work"
        work.mkdir(mode=0o777)
        work.chmod(0o777)
        scanner = next(row["digest_ref"] for row in pins["images"] if row["role"] == "scanner")
        command = ["docker","run","--rm","--pull=never","--network","ai-coding-sonar-internal",
            "--user","1000:1000","--cap-drop=ALL","--security-opt=no-new-privileges:true","--memory=2g","--cpus=2",
            "--mount",f"type=bind,src={stage},dst=/workspace,readonly",
            "--mount",f"type=bind,src={work},dst=/work",
            "--mount",f"type=bind,src={output / 'clippy.jsonl'},dst=/analysis/clippy.jsonl,readonly",
            "-w","/workspace","-e","SONAR_HOST_URL=http://server:9000","-e","SONAR_TOKEN",scanner,
            "-Dsonar.scanner.skipJreProvisioning=true","-Dsonar.scanner.javaExePath=/usr/bin/java",
            "-Dsonar.projectKey="+key,"-Dsonar.projectVersion="+proof["submission_commit"],
            "-Dproject.settings=/dev/null","-Dsonar.sources=crates","-Dsonar.inclusions="+",".join(proof["source_files"]),
            "-Dsonar.exclusions="+",".join(EXCLUSIONS),"-Dsonar.scm.disabled=true",
            "-Dsonar.rust.clippy.enabled=false","-Dsonar.rust.clippyReport.reportPaths=/analysis/clippy.jsonl",
            "-Dsonar.working.directory=/work","-Dsonar.scanner.metadataFilePath=/work/report-task.txt"]
        result = subprocess.run(command,env={**os.environ,"SONAR_TOKEN":token},capture_output=True,text=True,timeout=600)
        (output / "scanner.log").write_text(redact(result.stdout+result.stderr,{token,private["token"],private["password"]}))
        if result.returncode:
            raise RuntimeError("Scanner failed; see redacted scanner.log")
        if rust_manifest(stage) != before:
            raise RuntimeError("Analysis source changed")
        task = dict(line.split("=",1) for line in (work / "report-task.txt").read_text().splitlines() if "=" in line)
        if task.get("projectKey") != key:
            raise ValueError("Scanner task project differs from the snapshot binding")
        client = SonarClient("http://127.0.0.1:9000",private["token"])
        report = collect(client,task["ceTaskId"],key,output / "api",VERSION)
        if not report["analysis_ok"]:
            raise RuntimeError("Sonar background analysis failed")
        # Verify complete Rust file coverage through component identities, not only aggregate ncloc.
        components = []
        for page in range(1,21):
            payload = client.get("/api/components/tree",component=key,qualifiers="FIL",ps=500,p=page)
            components.extend(payload["components"])
            if page*500 >= payload["paging"]["total"]:
                break
        else:
            raise ValueError("Sonar component count exceeds budget")
        actual = {c["path"] for c in components if c.get("language") == "rust"}
        (output / "components.json").write_text(json.dumps(components,indent=2)+"\n")
        if actual != set(proof["source_files"]):
            raise ValueError("Sonar Rust components differ from the bound snapshot source manifest")
        verify_protocol(client,protocol)
        report.update(protocol_sha256=proof["protocol_sha256"],snapshot_binding_verified=True,rust_coverage_verified=True,snapshot_sha256=proof["snapshot_sha256"],
                      scanner_version=proof["scanner_version"],source_exclusions=list(EXCLUSIONS),
                      source_file_count=len(actual),clippy_returncode=0,clippy_report_sha256=proof["clippy_report_sha256"])
    except (OSError,ValueError,RuntimeError,KeyError,subprocess.SubprocessError) as error:
        report.update(analysis_ok=False,failure_category="sonar_analysis_failure",error=redact(str(error),{v for v in (token,private.get("token"),private.get("password")) if v}))
    finally:
        if token_name:
            try:
                request(private["password"],"/api/user_tokens/revoke",name=token_name)
            except RuntimeError:
                report.update(analysis_ok=False,failure_category="sonar_analysis_failure",error="Scanner token revocation failed; revoke the saved project token name before retrying")
                report["unrevoked_token_name"] = token_name
        report["duration_seconds"] = time.monotonic()-started
        (output / "sonar.json").write_text(json.dumps(report,indent=2)+"\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run",type=Path)
    parser.add_argument("--kind",choices=("base","solution"),default="solution")
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--credentials",type=Path,required=True)
    args = parser.parse_args()
    sys.path.insert(0,str(ROOT / "vendor/SWE-Milestone"))
    result = scan(args.run.resolve(),args.output.resolve(),args.credentials.resolve(),args.kind)
    print(json.dumps({key:result.get(key) for key in ("analysis_ok","failure_category","error","snapshot_binding_verified","rust_coverage_verified")}))
    raise SystemExit(0 if result["analysis_ok"] else 2)
