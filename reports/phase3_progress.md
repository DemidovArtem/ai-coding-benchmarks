# Phase 3 progress

Status: **not complete; quota gate stopped before the measured cohort**. No measured skill trial has started and no skill correctness/quality result is claimed. Phase 2 remains unchanged.

The owner approved the exact Rust component download and local build. The shared runtime is `sha256:3407cf8372c295e58722ff3ce33a0797e59e768cdaec496e20a15ef876505269`: Rust/rust-analyzer/rust-src 1.88.0, Python 3.13.14, Serena 1.6.1, Node v24.19.0. Two unprivileged, no-network, no-credential MCP probes returned the neutral fixture's Rust symbol.

| Profile | Activation on the shared image | Measured task |
| --- | --- | --- |
| baseline | Clean-profile audit reused; new matched run required | Not started |
| ponytail | Native SessionStart full mode observed by Codex; audit UID 1000 | Not started |
| caveman | Native SessionStart canonical caveman mode observed by Codex; audit UID 1000 | Not started |
| serena | MCP process and initial_instructions worked; first symbol call failed; corrected env verified offline only | Not started |

The first Serena Codex smoke exposed a real integration difference: MCP did not inherit the image's Cargo PATH or Rustup home. The installed rust-analyzer existed, but the server could not find it. The failed attempt, raw trace and usage are preserved. Its 78430 input / 65152 cached input / 184 output tokens are setup overhead, not measured task usage. The corrected child env explicitly pins the existing toolchain paths and offline mode; it changes no benchmark quarantine, host settings or image download budget.

The second Codex smoke stopped before any model invocation at the configured quota gate. The latest approximate reading is **89% primary / 21% secondary**, with a stop threshold of **85%**. Primary reset: **2026-10-20 00:52:22 Europe/Zurich** (2026-10-19 22:52:22 UTC). A later run must re-read live limits; the reset time alone does not authorize a model request.

`experiment.skill_trial` rejects an unverified or mismatched image/profile, freezes a separate cohort only after every activation proof passes, uses the unchanged task and grader, rejects profile/memory paths in the grader snapshot, and preserves failed activation separately from grader correctness. Its new fingerprint prevents pairing the Phase 3 skills with the older Phase 2 baseline. [Predeclared protocol and commands](phase3_protocol.md), [machine-readable progress](phase3_progress.json), [Serena evidence](serena_activation.json).

Next: with verified quota below 85%, repeat only the corrected Serena activation in a new output directory. After a real Rust-symbol call succeeds, freeze the cohort and run a new baseline, Ponytail, Caveman and Serena sequentially. Collect Git/usage/Sonar for each terminal run. No additional download permission is pending. Continuous work remains separately deferred with its documented dispatch blocker; Phase 6 is not running.

Additional zero-model check: the corrected MCP env also served `SearcherBuilder` from the full initial ripgrep workspace in 23.79 seconds, under UID 1000 with network disabled and no credentials. Every initial Rust file was verified byte-for-byte after the call. Only the nonregular `HomebrewFormula` link was omitted from the disposable export. No probe project state or memories enter measured trials. [Workspace proof](serena_ripgrep_offline.json). This strengthens Rust-workspace readiness; it does not replace the still-blocked Codex activation smoke.
