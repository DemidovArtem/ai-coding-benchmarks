"""Snapshot-bound Python Sonar analysis, separate from the frozen Rust protocol."""

import argparse
import hashlib
import json
from pathlib import Path
import os
import subprocess
import sys
import tarfile
import time

from experiment.collect import load
from experiment.python_metrics import source_filter, verify_snapshot
from experiment.runner import ROOT, save
from experiment.security import redact
from experiment.sonar import SonarClient, collect, project_key
from experiment.sonar_bootstrap import request
from experiment.sonar_scan import extract

PROTOCOL = ROOT / 'profiles/scikit_runtime/sonar_protocol.json'


def current_protocol(client):
    plugin = next(p for p in client.get('/api/plugins/installed')['plugins'] if p['key'] == 'python')
    profile = next(p for p in client.get('/api/qualityprofiles/search', language='py')['profiles']
                   if p['isDefault'] and p['name'] == 'Sonar way')
    rules = client.get('/api/rules/search', qprofile=profile['key'], activation='true', ps=500, f='actives')
    if rules['total'] > 500:
        raise ValueError('Python active-rule set exceeds the frozen collection budget')
    return {'server_version': client.get('/api/server/version'),
            'plugin': {k: plugin[k] for k in ('key', 'version', 'hash')},
            'profile': {k: profile[k] for k in ('key', 'name', 'language', 'activeRuleCount')},
            'active_rules_sha256': hashlib.sha256(json.dumps(rules['actives'], sort_keys=True).encode()).hexdigest(),
            'python_version': '3.11', 'coverage': 'captured production .py only; Cython excluded',
            'clippy': 'not applicable; no external linter imports'}


def scan(run, output, kind='solution'):
    started = time.monotonic()
    output.mkdir(parents=True, exist_ok=False)
    private = load(ROOT / 'results/sonar/private/credentials.json')
    client = SonarClient('http://127.0.0.1:9000', private['token'])
    protocol = load(PROTOCOL)
    if current_protocol(client) != protocol:
        raise ValueError('Python Sonar analyzer, default profile, or active rules changed')
    sidecar = load(run / 'evaluation/source_snapshot.integrity.json')
    repo = run / 'metrics_repository'
    if not repo.exists():
        subprocess.run(['git', 'clone', '--bare', '--quiet', str(run / 'repository.bundle'), str(repo)],
                       check=True, capture_output=True)
    captured = verify_snapshot(run / 'evaluation/source_snapshot.tar', sidecar, repo)
    capture = sidecar['capture_filter']
    selection = source_filter({'repo_src_dirs': capture['src_dirs'], **{k: capture[k]
                              for k in ('test_dirs', 'exclude_patterns', 'generated_patterns')}})
    files = {p: sha for p, sha in captured.items() if p.endswith('.py')
             and selection.is_src_file(p) and not selection.is_generated_file(p)}
    if not files:
        raise ValueError('No captured production Python source')
    stage = output / 'source'
    stage.mkdir()
    with tarfile.open(run / 'evaluation/source_snapshot.tar') as archive:
        extract(archive, stage)
    identity = sidecar['snapshot_sha256']
    key = project_key('scikit-common-base' if kind == 'base' else run.name, identity)
    existing = client.get('/api/projects/search', projects=key)['components']
    if not existing:
        request(private['password'], '/api/projects/create', project=key, name=key, visibility='private')
    elif len(existing) != 1 or existing[0].get('visibility') != 'private':
        raise ValueError('Python snapshot project must remain private')
    token_name = key + '-scanner'
    token = None
    report = {'analysis_ok': False, 'metrics': None, 'failure_category': 'sonar_analysis_failure'}
    binding = {'kind': kind, 'trial_id': run.name, 'project_key': key, 'snapshot_sha256': identity,
               'submission_commit': sidecar['agent_tag_commit'], 'source_files': files,
               'protocol_sha256': hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
               'source_scope': protocol['coverage']}
    save(output / 'binding.json', binding)
    try:
        token = request(private['password'], '/api/user_tokens/generate', name=token_name,
                        type='PROJECT_ANALYSIS_TOKEN', projectKey=key)['token']
        work = output / 'scanner_work'
        work.mkdir(mode=0o777); work.chmod(0o777)
        pins = load(ROOT / 'sonar/setup_candidates.json')
        scanner = next(r['digest_ref'] for r in pins['images'] if r['role'] == 'scanner')
        command = ['docker', 'run', '--rm', '--pull=never', '--network', 'ai-coding-sonar-internal',
            '--user', '1000:1000', '--cap-drop=ALL', '--security-opt=no-new-privileges:true', '--memory=2g', '--cpus=2',
            '--mount', f'type=bind,src={stage},dst=/workspace,readonly', '--mount', f'type=bind,src={work},dst=/work',
            '-w', '/workspace', '-e', 'SONAR_HOST_URL=http://server:9000', '-e', 'SONAR_TOKEN', scanner,
            '-Dsonar.scanner.skipJreProvisioning=true', '-Dsonar.scanner.javaExePath=/usr/bin/java',
            '-Dsonar.projectKey=' + key, '-Dsonar.projectVersion=' + sidecar['agent_tag_commit'],
            '-Dproject.settings=/dev/null', '-Dsonar.sources=sklearn', '-Dsonar.inclusions=' + ','.join(files),
            '-Dsonar.python.version=3.11', '-Dsonar.scm.disabled=true', '-Dsonar.working.directory=/work',
            '-Dsonar.scanner.metadataFilePath=/work/report-task.txt']
        result = subprocess.run(command, env={**os.environ, 'SONAR_TOKEN': token}, capture_output=True, text=True, timeout=900)
        (output / 'scanner.log').write_text(redact(result.stdout + result.stderr,
                                                   {token, private['token'], private['password']}))
        if result.returncode:
            raise RuntimeError('Python scanner failed; inspect redacted scanner log')
        task = dict(l.split('=', 1) for l in (work / 'report-task.txt').read_text().splitlines() if '=' in l)
        if task.get('projectKey') != key:
            raise ValueError('Python scanner task belongs to a different project')
        report = collect(client, task['ceTaskId'], key, output / 'api', protocol['server_version'])
        if not report['analysis_ok']:
            raise RuntimeError('Python Sonar background analysis failed')
        components = []
        for page in range(1, 21):
            payload = client.get('/api/components/tree', component=key, qualifiers='FIL', ps=500, p=page)
            components.extend(payload['components'])
            if page * 500 >= payload['paging']['total']:
                break
        else:
            raise ValueError('Python Sonar component count exceeds budget')
        save(output / 'components.json', components)
        actual = {r['path'] for r in components if r.get('language') == 'py'}
        if actual != set(files):
            raise ValueError('Sonar Python component coverage differs from captured production source')
        if any(hashlib.sha256((stage / p).read_bytes()).hexdigest() != sha for p, sha in files.items()):
            raise ValueError('Python source changed during analysis')
        if current_protocol(client) != protocol:
            raise ValueError('Python Sonar protocol changed during analysis')
        report.update(snapshot_sha256=identity, snapshot_binding_verified=True, python_coverage_verified=True,
                      source_file_count=len(files), protocol_sha256=binding['protocol_sha256'], source_scope=protocol['coverage'],
                      scanner_version=pins['scanner_version'], source_exclusions=[])
    except (OSError, ValueError, RuntimeError, KeyError, subprocess.SubprocessError) as error:
        report.update(analysis_ok=False, failure_category='sonar_analysis_failure',
                      error=redact(str(error), {v for v in (token, private['token'], private['password']) if v}))
        raise
    finally:
        report['total_duration_seconds'] = time.monotonic() - started
        if token:
            try:
                request(private['password'], '/api/user_tokens/revoke', name=token_name)
            except RuntimeError:
                report.update(analysis_ok=False, unrevoked_token_name=token_name)
                save(output / 'sonar.json', report)
                raise
        save(output / 'sonar.json', report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('--kind', choices=('base', 'solution'), default='solution')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT / 'vendor/SWE-Milestone'))
    result = scan(args.run.resolve(), args.output.resolve(), args.kind)
    print(json.dumps({k: result.get(k) for k in ('analysis_ok', 'python_coverage_verified', 'source_file_count')}))
    raise SystemExit(0 if result['analysis_ok'] else 2)


if __name__ == '__main__':
    main()
