# Verified benchmark container cleanup — 8 November 2026

The maintainer authorized cleanup of old benchmark containers after preservation checks and asked to start the second-repository experiment. Exactly six stopped benchmark containers were removed. No image, Docker volume, Sonar data, or unrelated project was deleted.

Observed free space on the Docker filesystem increased from **15,767,674,880** to **29,760,720,896 bytes**: **13,993,046,016 bytes** recovered. This is an observed filesystem change, not a sum of virtual image sizes. Concurrent host activity can affect the exact difference. The private backup directory occupies about 122 MiB on the workspace filesystem, which still has only about 2.4 GiB available.

## Preservation and verification

Private archives live under ignored `results/storage_cleanup/20261108/`, with directory permissions 0700. Each container has a source/home archive, an auxiliary archive of temporary diagnostics and root CLI state, a file-hash manifest, and closed SQLite backups where databases exist. Archives were read back and checked against all retained regular-file hashes. Restored source repositories passed `git fsck --full`; native rollout JSONL parsed successfully; every closed SQLite backup passed `PRAGMA integrity_check`.

The only omitted source/home data are rebuildable Rust `target/` outputs and the OAuth `auth.json` copy. The host authentication file remains intact. Absolute executable symlinks remain in the archives but were not extracted during verification. Exact original image IDs remain available; recreating package/tooling setup may still require the retained recipes and manifests.

All seven latest sixth-step checkpoints were separately verified: bundle clone and Git integrity, submission-tag commit identity, grader snapshot SHA-256, native rollout SHA-256, and all 13 Serena memory-file hashes. These checks preserve the inputs to continuation. They do **not** constitute a fresh native-session inference or a new experimental result.

| Removed container | Archived native rollouts | Archived Serena memories |
| --- | ---: | ---: |
| phase6g_serena_r01 preparation | 0 | 0 |
| phase6d_restore_baseline_r01 probe | 1 | 0 |
| phase6c_caveman_r02 failed preparation | 0 | 0 |
| phase6_serena_r01 historical runner | 1 | 11 |
| phase5_ponytail_r01 historical runner | 1 | 0 |
| phase3_serena_001 historical runner | 1 | 0 |

The 11 memories in the historical Serena container are distinct from the 13 verified files in its latest sixth-step checkpoint. Neither set was replaced by the other. Historical failures and all result rows remain intact.

## Restoring archived material

Keep the private archives local. Verify their SHA-256 against the private manifests and the public [cleanup record](storage_cleanup_20261108.json). Extract regular files and directories into a new staging directory with Python's `tarfile` data filter; do not extract absolute executable links onto the host. Recover source and uncommitted state from `testbed/`, session/configuration state from `fakeroot/`, and prefer the closed SQLite backups over raw database/WAL copies. Use the pinned original runtime and the existing stage-specific continuation procedure. Public patches restore source only; they cannot restore authenticated session state.

## Next experiment

The scikit-learn matrix remains four configurations, six changes and two cold repetitions: 48 planned submissions, **zero completed**. Acquisition will keep the common base and only the current grader, rather than download the complete 14.46 GB compressed collection. The initial pair has 4,005,763,625 unique compressed bytes. Expanded occupancy, build reserve and workspace growth still need checks before inference. Stop acquisition or execution before exhausting the disk; do not remove further experiment state merely to make a run fit.
