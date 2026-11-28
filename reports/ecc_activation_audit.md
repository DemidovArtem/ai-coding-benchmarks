# Retained ECC activation and checkpoint audit

Verified on 28 November 2026 without model inference. This audit reads private retained artifacts; a public clone cannot reproduce native history from patches alone. Original trial records, scores and activation fields are unchanged.

## ECC activation was used on measured tasks

The reviewed ECC 2.2.3 source commit, all profile-file hashes, 1,770 installed source/dependency files and pinned Node hash match the retained inputs. Native developer messages contain the official SessionStart Rust project context. Native tool records show real skill reads and explorer/reviewer delegation, rather than registration alone. Model and reasoning settings match the pinned gpt-6.1-sol/high throughout the retained agent tree.

| Edit | Newly observed child agents | Skill-read calls with retained output | Verified checkpoint files | ECC state files |
| --- | ---: | ---: | ---: | ---: |
| 1 | 2 | 4 | 7 | 1 |
| 2 | 3 | 3 | 11 | 2 |
| 3 | 3 | 3 | 15 | 3 |
| 4 | 3 | 3 | 19 | 4 |
| 5 | 2 | 3 | 27 | 10 |
| 6 | 3 | 3 | 31 | 11 |

Child counts are new native sessions at each checkpoint. Skill-call counts deduplicate inherited/forked tool calls and exclude earlier checkpoints. They count read commands with retained outputs, not every skill mentioned in context. State-file counts include ECC operational state, not just human-readable notes. Cumulative hook contexts establish activation; they are not a measured count of hook executions on every resume.

The `native_hook_activation_verified=false` and `subagent_activation_verified=false` fields in the original measured effective profiles were initialized during installation and were not replaced by a measured-task activation audit. They do not establish non-use. The independent smoke proved activation earlier; the retained measured traces now independently establish actual usage. Keep these evidence types separate.

## Checkpoint integrity

All six ECC checkpoints pass Git fsck, exact starting-tree and submission-tag checks, parent ancestry, byte-for-byte snapshot comparison against Git, incremental/cumulative patch comparison, checkpoint hashes and full SQLite integrity checks. Root identity is unchanged; previous native rollout bytes remain prefixes of subsequent captures. Every retained native root/child thread exists in the closed database. Native unique-response usage and known per-step totals agree; originally missing reasoning-token totals remain missing.

The three scikit-learn first-step checkpoints also pass common/incremental bundle hashes, Git integrity, source/snapshot/patch binding, native identity, closed SQLite hashes/integrity and usage-counter checks. Their original runtime has not been restored.

## Interpretation and reproduction boundary

The completed six-edit ECC result remains one interrupted/recovered trajectory: two accepted boundaries, three rejected and one unavailable grader score. This audit does not rerun inference, change grader outcomes, prove fresh-host execution or establish statistical superiority. Memory files and native history are preserved; this is not a claim that every retained note was read on every task.

[Machine-readable evidence](retained_checkpoint_audit.json) binds each check to the original record SHA-256 and references native call IDs. The audit used the retained Git bundles and snapshots, `experiment.ecc.native_evidence`, `experiment.metrics.codex_usage`, the existing footprint collector event reader and read-only SQLite `integrity_check`. No evaluator or quarantine was modified.

[ECC results](ecc_results.md) · [Current roadmap](../docs/ROADMAP.md) · [Live register](../EXPERIMENT_STATUS.md)
