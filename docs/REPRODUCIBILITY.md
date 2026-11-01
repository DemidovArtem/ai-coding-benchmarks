# Reproducibility and execution

There are three different operations: re-analyzing public results, reproducing a fresh model trial, and resuming an existing authenticated session. Only the first is available directly from a public clone. Model outputs are not deterministic.

## Public analysis and local checks

Use Linux, Git, Python 3.12+, and a virtual environment. From the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-setup.txt -r requirements-plots.txt
.venv/bin/python docs/render_results.py
```

The analysis renderer checks uniqueness, task coverage, and summary ranges before plotting tracked `reports/plots/current_comparison.json`. It preserves the context-amendment disclosure and does not overwrite frozen figures or canonical records. Dependencies for this public path are separate from frozen experiment requirements.

Published patches and [`reports/patches/manifest.json`](../reports/patches/manifest.json) expose source differences and Git bindings. A patch applies only to the exact initial/parent source tree recorded in its manifest. Incremental and cumulative patches have different bases; do not apply both on top of one another.

## Acquire pinned benchmark sources

These commands download public sources, not Docker images or model output. Inspect upstream licenses first. Use absent destination directories and run from the repository root:

```bash
git clone https://github.com/DeepCommit-ai/SWE-Milestone.git vendor/SWE-Milestone
git -C vendor/SWE-Milestone checkout 17a8f1593e172e26b36cea15e2b30fb9536c93f5
git -C vendor/SWE-Milestone switch -c experiment/oauth-profiles
git -C vendor/SWE-Milestone apply ../../patches/swe-milestone-oauth.patch
git -C vendor/SWE-Milestone add -u
git -C vendor/SWE-Milestone commit -m "fix(codex): isolate profiles and pin milestone CLI"
```

The checkout and patch above are sufficient for the local test suite. Dataset acquisition below is needed for actual benchmark tasks, not for tests or public plotting:

```bash
git -c filter.lfs.smudge= -c filter.lfs.required=false clone --depth 1 --branch v1.0.2 https://huggingface.co/datasets/DeepCommit-ai/SWE-Milestone-data results/setup/dataset
git -C results/setup/dataset sparse-checkout set BurntSushi_ripgrep_14.1.1_15.0.0 config
git -C results/setup/dataset rev-parse HEAD
```

Dataset HEAD must be `3500478e740d42583277c2658aa7729eb36e10f4`. Reject LFS pointers in place of source data. The patched upstream Git tree must match the frozen config; its local commit ID can differ because author/date metadata differ. Do not change the evaluator, hidden tests, scoring, or quarantine to make a run pass.

## Local test suite

The full test suite imports public SWE-Milestone helpers. Complete the upstream checkout/patch commands above first; the dataset clone is unnecessary for these local tests. Then run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=vendor/SWE-Milestone .venv/bin/python -m unittest discover -s tests
```

Tests use fixtures and mocks without model inference, Docker, or private trial records. Two tests require temporary loopback sockets. `requirements-dev.txt` is optional for pytest-based development. Passing tests does not prove a fresh model environment is ready.

## Runtime prerequisites for new inference

Actual trials additionally require Docker, ChatGPT OAuth, Codex CLI 0.163.0, the recorded Node/Rust tooling, task-specific grader images, and the runtime closure referenced by the chosen frozen protocol. Existing runners explicitly reject paid API-key environments. Receiving API credits would support a separately specified API cohort; API-funded execution is not implemented by this documentation change.

[`profiles/runtime/Dockerfile`](../profiles/runtime/Dockerfile) and manifests record the original local closure, including Python 3.13.14, Serena 1.6.1, Node v24.19.0, and Rust 1.88.0. The Dockerfile expects staged `python/`, `site-packages/`, and `node` inputs; it is not a self-contained network installer. Later offline runtimes retain exact CLI/Node assets. Several scripts and configs refer to original local paths and immutable image IDs. A clean machine needs environment reconstruction and a new setup audit before inference; those steps are not yet a portable bootstrap command.

Do not silently substitute current package versions or runtime images in a historical cohort. If inputs differ, record a new cohort with its own matched baseline.

With the correct local environment restored, inspect the configuration and run read-only checks:

```bash
.venv/bin/python -m experiment.audit --output /tmp/ai-coding-environment.json
.venv/bin/python -m experiment.quota --output /tmp/ai-coding-quota.json
.venv/bin/python -m experiment.runner --help
```

A successful audit is not a benchmark result. Check source pins, live quota, disk, profile activation, grading image closure, and quarantine before a model call. Use a fresh output directory. The historical isolated entry point is `experiment.runner trial --variant baseline --output <new-directory>`; its default frozen configuration is not the current seventh-step continuation. Continuous phase modules are deliberately phase-specific and can launch paid-in-quota model work immediately; inspect their protocols and prerequisites before invoking them.

## Local SonarQube

[`sonar/compose.yaml`](../sonar/compose.yaml) pins the image and uses `pull_policy: never`. On the prepared local host:

```bash
docker compose -f sonar/compose.yaml up -d server
.venv/bin/python -m experiment.sonar_proxy
```

The second command is a foreground loopback relay for this host's Docker/internal-network behavior; do not start it if port 9000 already works. A fresh machine must acquire the pinned images first. Deployment uses an internal Docker network and local credentials, never public authentication data in Git.

Evaluation is snapshot-based, not an arbitrary latest-source scan. [`experiment/sonar_scan.py`](../experiment/sonar_scan.py) validates snapshot/tag binding, stages source, runs offline Clippy and the scanner, waits for the server task, and verifies Rust coverage. Inspect its interface with `.venv/bin/python -m experiment.sonar_scan --help`. The full commands and credential setup are in [`sonar/README.md`](../sonar/README.md). Analyzer estimates are not human-review measurements.

## Private state and resuming

Ignored `results/` contains canonical JSONL, raw traces, snapshots, source bundles, native session histories/SQLite stores, and Serena memories. Credentials remain private. Those artifacts are not supplied by a public clone. Public patch replay restores code only; it cannot recreate reasoning state or authenticated session history.

On the maintainer's retained environment, stage-specific checkpoint manifests and restore functions verify hashes, exact sessions, source tags, and memory policy before continuation. Seventh-step preparation currently has 0/7 completed continuations. Do not rerun a prefix or treat a recovery attempt as an independent repetition.

The maintainer regenerates the live register from retained records using `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m experiment.status`. That command requires ignored canonical records and is not part of the clean-clone quickstart.
