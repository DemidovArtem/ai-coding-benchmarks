# Scikit-learn v2 common runtime

This independent image serves all five methods in `scikit-five-method-v2`.
It does not claim to reproduce the deleted historical runtime or continue its
three submissions. The [manifest](manifest.json) records the new image ID,
source inventories, offline Python MCP proof and retained archive identity.

The ignored durable context is `results/scikit_v2_runtime_build/context`.
It contains only the reviewed public Codex 0.163.0 release, Python 3.13.14 and
Serena 1.6.1 dependency closure, Pyright, both pinned Node binaries and the
[SHA256-pinned Debian packages](../../reports/scikit_v2_package_budget.json).
All 72 distribution versions matched the historical package pins. No host
settings, authentication, project memories or unrelated caches were staged.
Node 24.19.0 remains the hook/Pyright binary; ECC uses Node 24.22.1. Every method
gets the same image, regardless of which optional profile it activates.

Build only from the verified retained context, without network access:

```sh
docker build --network=none --pull=false \
  -f profiles/scikit_runtime_v2/Dockerfile \
  -t ai-coding-scikit-v2:20261128 results/scikit_v2_runtime_build/context
```

The durable `common-runtime.docker.tar` archive lives next to the context,
outside Docker's cache. Its full SHA256, configuration hash and every unpacked
layer hash have been verified against the image identity. Keep it until the
cohort and publication are complete. It can be restored with `docker load -i`
after checking its recorded SHA256; a destructive cache-loss recovery has not
been exercised. The archive and context are local research assets, not shipped
in the public Git repository.

Validation so far covers the offline build and a real, unprivileged, credential-free
`get_symbols_overview` MCP call on a neutral Python fixture with `--network none`.
It does not establish activation during a model task, grader readiness, or a
completed fresh benchmark. Those have separate gates in the approved plan.
