# Isolated Ponytail profile

This profile stages the reviewed native hook closure from installed upstream Ponytail **5.3.2**, MIT licensed. `manifest.json` pins every source file and the already installed Node **v24.19.0** executable by SHA-256. Node is copied into this profile's container; no Node download, npm install or global settings change is required. The baseline image itself remains unchanged.

`native_hooks.json` preserves upstream SessionStart, UserPromptSubmit and SubagentStart events. The dispatcher selects Codex behavior with dedicated PLUGIN_DATA, sets full mode, verifies the entire source/runtime closure before each hook and runs as the unprivileged container user. The default bounded codebase map remains enabled. Claude statusline/band import and other-host integrations are unreachable in the Codex branch and are not staged.

The profile uses local native user hooks, with plugins, remote plugins, apps and web tools still disabled. [Official OpenAI hook documentation](https://learn.chatgpt.com/docs/hooks) documents native hook discovery, exact-definition trust and the one-invocation `--dangerously-bypass-hook-trust` option for automation that reviews sources externally. This profile uses that option only inside the isolated container after reviewing/pinning hook sources. It does not persist host trust or change host configuration.

The installer first verifies the same clean baseline isolation/quarantine conditions, then copies the pinned runtime and assets to root-owned, non-writable `/opt/experiment-*` paths. Hook execution is never elevated. The dispatcher audit records only event, mode, output size/hash and UID; it does not save the prompt or credentials.

A real OAuth smoke observed **PONYTAIL MODE ACTIVE — level: full**, with native hook audit and zero tool calls. [Activation evidence](../../reports/ponytail_activation.json) includes token usage and durable raw-log location. The fixture contains one neutral Rust file and is mounted read-only. No benchmark SRS, earlier implementation or grader feedback is supplied.

```bash
PYTHONPATH=vendor/SWE-Milestone .venv/bin/python -m experiment.skill_smoke --output /tmp/ai-coding-experiment/unique_ponytail_activation
```

The smoke is an activation test, not a measured benchmark trial. An earlier no-network/no-credential app-server probe only listed configured hooks; no SessionStart ran, and it was not treated as activation. Measured skill A/B remains pending. Caveman and Serena must use separate profiles and activation evidence.
