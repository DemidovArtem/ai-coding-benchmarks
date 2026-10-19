# Common runtime for the skill cohort

The planned shared image derives from the approved, digest-pinned ripgrep base-offline image. It adds only public tooling prerequisites: the already installed Python **3.13.14**, Serena **1.6.1** and its 72 installed distributions, the already installed Node **v24.19.0**, and Rust **1.88.0** rust-analyzer/rust-src components. Style hooks, MCP registration and memories remain profile-specific; the baseline activates none of them. A fresh matched baseline must use the same common runtime image as the skill variants.

The local Python/dependency closure has **8025 files/symlinks**, **177213446 file bytes**, excluding bytecode caches. `manifest.json` pins its complete inventory SHA and records exact distribution versions. Source files are copied only from the installed interpreter/tool environment. No user settings, host Serena projects, memories, credentials or auth files enter the build context. Node comes from the bundled runtime and is independently hashed.

A no-network, no-credential container probe successfully loaded the relocated Python runtime and Serena CLI from a read-only mount in the approved base image. This proves runtime import compatibility, not Rust language-server or MCP activation.

The remaining component download is **11773236 compressed bytes** (about 11.8 MB), from the dated official Rust 1.88.0 release. [Download budget](download_budget.json) records exact URLs, SHA-256 and Content-Length obtained without downloading component payloads. The build does not pull a new base image and does not install Python packages from the network.

**Approval pending:** automatic approval review rejected `docker build` because `rustup component add` performs a new download. The owner has been asked to authorize these exact components and the local image build. Do not build, download the component payloads or work around that rejection until the explicit answer arrives.

After approval, verify the staged context inventory, build with `--pull=false`, record the resulting immutable image ID and actual rust-analyzer/Python/Serena versions, then test Rust symbols/MCP entirely offline before any measured skill trial. Freeze one cohort setup fingerprint only after all profile activation assertions pass. Neither a listed MCP server nor a CLI `--help` result is language-server activation evidence.

The staged context is `/tmp/ai-coding-serena-runtime`; the inventory is also pinned there. Preserve these artifacts or recreate the exact recorded local package closure before rebuilding. The build recipe is `profiles/runtime/Dockerfile`. No host sysctl, firewall, global Codex configuration or benchmark quarantine change is part of this setup.
