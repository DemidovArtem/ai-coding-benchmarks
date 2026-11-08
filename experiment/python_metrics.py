"""Physical production LOC for the separate Python/Cython cohort."""

from pathlib import Path, PurePosixPath
import hashlib
import tarfile

from experiment.metrics import git, parse_numstat

EXTENSIONS = ('.py', '.pyx', '.pxd', '.pxi')


def source_filter(metadata):
    from harness.utils.src_filter import SrcFileFilter
    return SrcFileFilter(src_dirs=metadata['repo_src_dirs'], test_dirs=metadata['test_dirs'],
                         exclude_patterns=metadata.get('exclude_patterns'),
                         generated_patterns=metadata.get('generated_patterns'))


def production(path, selection):
    return bool(path and Path(path).suffix in EXTENSIONS and selection.is_src_file(path)
                and not selection.is_generated_file(path)
                and not {'vendor', 'generated', '__pycache__'}.intersection(Path(path).parts))


def footprint(repo, base, end, metadata):
    selection = source_filter(metadata)
    base = git(repo, 'rev-parse', '--verify', '--end-of-options', base + '^{commit}').decode().strip()
    end = git(repo, 'rev-parse', '--verify', '--end-of-options', end + '^{commit}').decode().strip()
    rename = '-M' + str(metadata.get('rename_threshold', 50)) + '%'
    options = ('--no-ext-diff', '--no-textconv', '--diff-algorithm=myers', rename)
    raw = parse_numstat(git(repo, 'diff', *options, '--numstat', '-z', base, end, '--'))
    fields = iter(git(repo, 'diff', *options, '--name-status', '-z', base, end, '--').split(b'\0'))
    result = dict(starting_commit=base, ending_commit=end, added_prod_loc=0, deleted_prod_loc=0,
                  changed_prod_files=0, new_prod_files=0, deleted_prod_files=0, renamed_prod_files=0,
                  binary_changes=[], files=[], rules={'extensions': list(EXTENSIONS),
                  'loc': 'physical lines including comments and blanks; no inline-test AST removal',
                  'excluded': ['metadata tests/exclusions/generated', 'vendor/generated/__pycache__ directories'],
                  'cython': 'included in footprint; excluded from Python Sonar and semantic coverage',
                  'rename_detection': rename})
    for status in fields:
        if not status:
            continue
        first = next(fields).decode(errors='surrogateescape')
        old, new = (first, next(fields).decode(errors='surrogateescape')) if status.startswith(b'R') else (first, first)
        counts = raw[(old, new)]
        before = status != b'A' and production(old, selection)
        after = status != b'D' and production(new, selection)
        row = dict(status=status.decode(), old_path=None if status == b'A' else old,
                   new_path=None if status == b'D' else new, raw_added=counts[0], raw_deleted=counts[1])
        result['files'].append(row)
        if counts[0] is None:
            result['binary_changes'].append(new or old)
            row['production_metrics'] = 'binary_excluded'
            continue
        if not before and not after:
            row['production_metrics'] = 'excluded'
            continue
        if before and after:
            added, deleted = counts
        else:
            added = len(git(repo, 'show', end + ':' + new).splitlines()) if after else 0
            deleted = len(git(repo, 'show', base + ':' + old).splitlines()) if before else 0
        row.update(added_prod_loc=added, deleted_prod_loc=deleted)
        result['added_prod_loc'] += added
        result['deleted_prod_loc'] += deleted
        result['changed_prod_files'] += int(bool(added or deleted or status.startswith(b'R')))
        result['new_prod_files'] += int(after and not before)
        result['deleted_prod_files'] += int(before and not after)
        result['renamed_prod_files'] += int(status.startswith(b'R') and before and after)
    total = 0
    for encoded in git(repo, 'ls-tree', '-r', '--name-only', '-z', end).split(b'\0'):
        path = encoded.decode(errors='surrogateescape')
        if production(path, selection):
            content = git(repo, 'show', end + ':' + path)
            if b'\0' not in content:
                total += len(content.splitlines())
    result.update(net_prod_loc=result['added_prod_loc'] - result['deleted_prod_loc'],
                  churn_prod_loc=result['added_prod_loc'] + result['deleted_prod_loc'], cumulative_prod_loc=total)
    return result


def verify_snapshot(snapshot, sidecar, repo):
    with Path(snapshot).open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != sidecar['snapshot_sha256'] or sidecar.get('ok') is not True:
            raise ValueError('Snapshot hash or capture integrity failed')
    end = sidecar['agent_tag_commit']
    if git(repo, 'rev-parse', sidecar['tag'] + '^{commit}').decode().strip() != end:
        raise ValueError('Snapshot tag changed')
    manifest = {}
    seen = set()
    with tarfile.open(snapshot) as archive:
        for member in archive:
            path = PurePosixPath(member.name.removeprefix('./'))
            if path.is_absolute() or '..' in path.parts or path in seen or not (member.isfile() or member.isdir()):
                raise ValueError('Unsafe or duplicate snapshot member')
            seen.add(path)
            if member.isfile():
                content = archive.extractfile(member).read()
                if content != git(repo, 'show', end + ':' + str(path)):
                    raise ValueError('Snapshot content differs from source commit: ' + str(path))
                manifest[str(path)] = hashlib.sha256(content).hexdigest()
    if not any(Path(p).suffix == '.py' for p in manifest):
        raise ValueError('Snapshot contains no Python source')
    return manifest
