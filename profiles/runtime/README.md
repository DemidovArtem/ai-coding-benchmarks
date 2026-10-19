# Common runtime for the skill cohort

The verified shared image derives from the approved, digest-pinned ripgrep base-offline image. It adds only public tooling prerequisites: the already installed Python **3.13.14**, Serena **1.6.1** and its 72 installed distributions, the already installed Node **v24.19.0**, and Rust **1.88.0** rust-analyzer/rust-src components. Style hooks, MCP registration and memories remain profile-specific; the baseline activates none of them. A fresh matched baseline must use the same common runtime image as the skill variants.

The local Python/dependency closure has **8025 files/symlinks**, **177213446 file bytes**, excluding bytecode caches. `manifest.json` pins its complete inventory SHA and records exact distribution versions. Source files are copied only from the installed interpreter/tool environment. No user settings, host Serena projects, memories, credentials or auth files enter the build context. Node comes from the bundled runtime and is independently hashed.

A no-network, no-credential container probe successfully loaded the relocated Python runtime and Serena CLI from a read-only mount in the approved base image. This proves runtime import compatibility, not Rust language-server or MCP activation.

The remaining component download is **11773236 compressed bytes** (about 11.8 MB), from the dated official Rust 1.88.0 release. [Download budget](download_budget.json) records exact URLs, SHA-256 and Content-Length obtained without downloading component payloads. The build does not pull a new base image and does not install Python packages from the network.

The owner explicitly approved both components and the local build. The build completed with `--pull=false`; no registry image or Python package was downloaded. The immutable image is `sha256:3407cf8372c295e58722ff3ce33a0797e59e768cdaec496e20a15ef876505269`. Its rust-analyzer reports `1.88.0 (6b00bc3 2025-06-23)`.

`experiment.serena_probe` verified all 8025 staged inventory entries, then started a fresh container with `--network none`, UID 1000, dropped capabilities, no credentials and a neutral Cargo fixture. A real stdio MCP `get_symbols_overview` call returned `activation_fixture`. The manifest binds this proof to the image ID. Raw artifacts: `/tmp/ai-coding-experiment/serena_offline_001`.

This offline proof establishes Rust LSP/MCP functionality. Separate OAuth activation smokes must still verify Ponytail, Caveman and Serena on this exact image before freezing the measured cohort. Measured trials use a new matched baseline on the same image; Phase 2 comparisons remain separate.

The staged context is `/tmp/ai-coding-serena-runtime`; the inventory is also pinned there. Preserve these artifacts or recreate the exact recorded local package closure before rebuilding. The build recipe is `profiles/runtime/Dockerfile`. No host sysctl, firewall, global Codex configuration or benchmark quarantine change is part of this setup.
