"""Export exact continuous Git diffs and a replay manifest; never start a trial."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
OUTPUT=ROOT/'reports/patches'


def git(repo,*args,env=None):
    return subprocess.check_output(['git','-C',str(repo),*args],env=env)


def main():
    from experiment.security import credential_values
    secrets=credential_values(Path.home()/'.codex/auth.json')
    rows=[json.loads(line) for line in (ROOT/'results/results.jsonl').read_text().splitlines() if line.strip()]
    OUTPUT.mkdir(exist_ok=True)
    manifest=[]
    for row in rows:
        continuous=row.get('continuous') or {}
        if row.get('trial_state')!='finished' or not continuous.get('trajectory_id') or row.get('collection_errors'):
            continue
        repo=Path(row['artifacts_path'])/'metrics_repository'
        bundle=Path(row['artifacts_path'])/'repository.bundle'
        end=row['ending_commit']
        target=git(repo,'rev-parse',end+'^{tree}').decode().strip()
        patches={}
        for kind,base in (('cumulative',row['starting_commit']),('incremental',continuous['input_commit'])):
            patch=git(repo,'diff','--binary','--full-index','--no-ext-diff','--no-textconv',base,end,'--')
            if any(secret.encode() in patch for secret in secrets if secret):
                raise ValueError('Credential detected; patch export withheld')
            with tempfile.TemporaryDirectory(prefix='verify-patch-') as tmp:
                env={**os.environ,'GIT_INDEX_FILE':str(Path(tmp)/'index')}
                git(repo,'read-tree',base,env=env)
                if patch:
                    subprocess.run(['git','-C',str(repo),'apply','--cached','--binary','--whitespace=nowarn','-'],
                                   input=patch,env=env,check=True,capture_output=True)
                if git(repo,'write-tree',env=env).decode().strip()!=target:
                    raise ValueError('Replayed patch differs from submitted tree')
            path=OUTPUT/(row['trial_id']+'.'+kind+'.patch')
            path.write_bytes(patch)
            patches[kind]={'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(patch).hexdigest(),
                           'base_commit':base,'tree_replay_verified':True}
        manifest.append({'trial_id':row['trial_id'],'variant':row['variant'],
                         'setup_fingerprint':row['setup_fingerprint'],'trajectory_id':continuous['trajectory_id'],
                         'step':continuous['step'],'repetition':row['repetition'],
                         'starting_commit':row['starting_commit'],'ending_commit':end,'ending_tree':target,
                         'snapshot_sha256':row['snapshot_sha256'],
                         'executor_session_id':continuous['executor_session_id'],
                         'local_bundle':str(bundle.relative_to(ROOT)),
                         'bundle_sha256':hashlib.sha256(bundle.read_bytes()).hexdigest(), 'patches':patches})
    (OUTPUT/'manifest.json').write_text(json.dumps({'entries':manifest,
        'limits':'Patches restore source trees, including benchmark test masking. They do not restore a Codex session or provide an implemented continuation runner.'},indent=2)+'\n')
    print('Exported and replay-verified',len(manifest)*2,'patches from',len(manifest),'immutable submissions.')


if __name__=='__main__':main()
