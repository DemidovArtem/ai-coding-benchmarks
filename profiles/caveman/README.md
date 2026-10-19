# Isolated Caveman profile

This treatment uses the upstream **communication skill** and native Codex SessionStart hook from JuliusBrussee/caveman **v4.0.1**, commit `d262ab3882952a59312ff3537cd86d894523c5ab`. Every staged file and the existing Node v24.19.0 runtime is pinned in `manifest.json`. Both upstream license files are retained.

The configured `CAVEMAN_DEFAULT_MODE=full` is an upstream legacy alias. Version 4.0.1 resolves it to **caveman** and emits `CAVEMAN MODE ACTIVE — mode: caveman`. This differs from the older local communication skill and the curated 2.7.0 workflow package. Neither is silently substituted. The benchmark does not enable a gateway, optimizer, MCP middleware, Cavecrew presets or unrelated Caveman skills.

The upstream repo-native hook/config/ruleset are copied unchanged. The dedicated user hook definition replaces only the launch path with the audited dispatcher. It verifies the source and runtime hashes, runs unprivileged, sets the configured mode and requires the complete pinned ruleset to appear. The raw native hook output is passed through to Codex. The wrapper records only activation metadata, mode, UID and context hash/length.

Native hooks are registered without enabling plugins, remote plugins, apps or web tools. The one-invocation hook-trust bypass is limited to the protected container after external source/hash review, as documented by [OpenAI](https://learn.chatgpt.com/docs/hooks). Host settings and trust remain unchanged. Upstream's [installation documentation](https://github.com/JuliusBrussee/caveman/blob/d262ab3882952a59312ff3537cd86d894523c5ab/INSTALL.md#codex) describes the SessionStart integration.

A real OAuth smoke observed the exact mode header and a native SessionStart audit with UID 1000, using a neutral read-only fixture and zero tools. [Activation evidence](../../reports/caveman_activation.json) retains its usage and durable artifact location. This is an activation test, not a measured benchmark result.

```bash
PYTHONPATH=vendor/SWE-Milestone .venv/bin/python -m experiment.skill_smoke --variant caveman --output /tmp/ai-coding-experiment/unique_caveman_activation
```
