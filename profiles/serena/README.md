# Isolated Serena profile — activation pending

`config.toml` registers exactly one local **stdio** MCP server, Serena **1.6.1**, using the relocated Python **3.13.14** runtime and pinned dependency closure. It uses `--project-from-cwd --context codex`; no host-global MCP setting is changed. Plugins, remote plugins, connected apps and web tools remain disabled.

The Serena home is dedicated to each fresh container: `/home/fakeroot/.serena-profile`. `server_config.yml` starts with no registered projects, no dashboard/GUI/browser, records tool usage and selects the local CHAR_COUNT estimator. It never uses the optional Anthropic API token estimator or downloads a tiktoken dictionary. `SERENA_USAGE_REPORTING=false` disables Serena's startup usage request. No host `.serena` directory, onboarding notes or memories are copied.

Each independent trial must start with zero project memories. Cold onboarding time/tokens belong to that trial; state may persist only across milestones of that same continuous trajectory. After a run, collect memory file count/bytes separately from production LOC and confirm that the unchanged source capture excludes `.serena` state. Never transfer onboarding knowledge from an earlier variant or repetition.

The owner approved the exact 11.8 MB Rust component download, and the shared image is built. An unprivileged, no-network, no-credential MCP probe returned a Rust symbol. [Runtime proof](../runtime/README.md), [version manifest](../runtime/manifest.json), [download URLs/hashes](../runtime/download_budget.json). An actual Codex MCP activation smoke on that image remains required before any measured Serena trial.

A future activation smoke may explicitly request one Serena tool call to prove connectivity. Measured trials must report natural usage, including zero calls, without inventing tool-use evidence. The recommended setup comes from [Serena's Codex client instructions](https://github.com/oraios/serena/blob/main/docs/02-usage/030_clients.md) and [memory policy documentation](https://github.com/oraios/serena/blob/main/docs/02-usage/045_memories.md); actual installed source/runtime versions are pinned locally.
