# Phase 6b runtime amendment before the first model turn

The initial baseline setup failed before source preparation or inference. The upstream installer requested `https://chatgpt.com/codex/install.sh`, which returned HTTP 404. The failed attempt `phase6b_baseline_r01_s01` remains in the result register; it is not a model observation.

The revised runtime is a child of the exact previously approved common image. It adds only the complete standalone Codex 0.163.0 release already installed in the retained Phase 6 Serena container. The payload includes the same native CLI, code-mode host, rg, bwrap and packaged runtime resources. The [payload manifest](codex_offline_payload.json) records every regular-file SHA-256 and internal symlink. No credentials, session history or memories are included. No registry images or other files were downloaded. The [Dockerfile](../profiles/runtime/codex_offline/Dockerfile) builds with network disabled and verifies the exact CLI version.

All workflows use this one revised image. The upstream installer detects the already installed requested version, skips its unavailable download URL and performs its normal credential setup. OAuth remains a read-only host mount. Rust, Node, Python, Serena, repository source, grading, quarantine and Sonar inherit the same parent image and frozen settings.

The runtime amendment passed a zero-model startup smoke. Before a replacement Phase 6b model run began, the user shortened the scope to three edits for baseline, Caveman and Ponytail. That active scope is frozen in `phase6c_experiment.json`; Phase 6b is superseded. The failed setup and zero-model diagnostics remain retained and add no independent observations to the means.

The old Phase 6 source, memories, submission tags and thread remain retained. An abandoned earlier Phase 5 plan attempt, already superseded by its completed retry, was archived locally with its source/Git bundle and Codex sessions before its container was removed to recover disk space. Only its regenerable Cargo target cache was omitted; credentials were not copied. This cleanup does not alter any measured result.
