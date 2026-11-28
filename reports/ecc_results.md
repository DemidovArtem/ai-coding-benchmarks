# ECC for Codex, offline: six-edit pilot results

One ripgrep trajectory completed all six tasks on 16 November 2026. This is n=1, not a statistically powered comparison. Historical cohorts remain separate.

The [28 November retained-evidence audit](ecc_activation_audit.md) verifies actual
measured skill/subagent use and source/native checkpoint integrity without new
inference. It explains the original false activation fields without rewriting
those records.

| Edit | Grader | Production churn vs start | Net production LOC | Input tokens, root + children | Output tokens, root + children | Sonar |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | Accepted | 37 | 1 | 2751421 | 13752 | Complete |
| 2 | Accepted | 134 | 92 | 3606335 | 22812 | Complete |
| 3 | Rejected | 187 | 131 | 4744820 | 15426 | Complete |
| 4 | Rejected | 242 | 178 | 5086994 | 14307 | Complete |
| 5 | Unavailable: known grader dependency | 269 | 191 | 7346095 | 18500 | Complete |
| 6 | Rejected | 560 | 468 | 13621901 | 38858 | Complete |

Two of five evaluable task boundaries were accepted. The fifth score is unavailable because the original grader requires an undeclared `max_matches` dependency. Preserve it as unknown, not a model failure or zero score. The third step introduced a `glob::tests::re35` P2P regression; later steps continue the accumulated code rather than resetting it. Task four also reports missing P2P tests, so its raw rejection should not be interpreted as a count of newly introduced bugs.

By edit six, cumulative production churn is 560 lines and net production growth is 468 lines. Total measured usage is 37,157,566 input tokens, including 36,146,304 cached input tokens, and 123,655 output tokens. Parent counters exclude child usage; native response IDs are deduplicated across the retained agent tree. Setup smoke and the zero-token OAuth rejection are excluded from these totals.

Final Sonar deltas versus the newly verified common base are +133 cognitive complexity, +115 cyclomatic complexity, +1 maintainability issue and +7 estimated remediation minutes. These aggregate snapshot deltas include benchmark test masking and inline tests; they are not production-only architectural quality measurements.

## Interruptions and interpretation

- Quota exhaustion interrupted edit three. The runner waited 12,347.68 seconds and resumed the same root session. A quota-aborted child was retained; checkpoint collection was repaired without rerunning inference.
- A host network change left a stale DNS resolver. The fourth-step gate stopped before inference. The current resolver was restored and the same pinned quarantine was reapplied and verified.
- The old OAuth token was revoked. A fourth-step attempt was rejected with 401; all 173 prior native response records and cumulative usage were unchanged. That failed attempt remains registered. A separately named continuation used the refreshed same-account OAuth credential and preserved the failed native turn.
- The Sonar relay became unavailable. The failed scan was preserved; only the unchanged source snapshot was reanalyzed after restoring the relay.
- No completed source prefix was replayed. Root identity, adjacent source ancestry, previous submission tags, snapshot hashes and all retained native/memory checkpoint hashes were verified after completion.

These checks establish artifact integrity and measured outcomes, not invariance to interruptions. Recovery prompts and failed turns are part of the preserved context. Network retries, cold or changed cache state and provider delays can affect elapsed time and token use. The recorded model time excludes the explicit quota wait but is not network-free compute time. Treat this as an interrupted, recovered exploratory trajectory; a clean independent repeat is needed before attributing efficiency differences to ECC.

[Metric curves](plots/mean_curves_f6334976.png) · [Protocol](ecc_protocol.md) · [Experiment register](../EXPERIMENT_STATUS.md) · [Patch replay manifest](patches/manifest.json)

Public curves and source-patch replay do not reproduce private native session state. No claim of statistical significance is made.
