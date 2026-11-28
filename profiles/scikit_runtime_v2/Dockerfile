FROM hyd2apse/swe-milestone__scikit-learn_scikit-learn_1.5.2_1.6.0__base-offline@sha256:2b77ce7d7030461e3e7ca67e47d910d7fa0e6784c7520c62f183ebcde837bd0a

COPY python /opt/experiment-serena/python
COPY site-packages /opt/experiment-serena/site-packages
COPY pyright /opt/experiment-pyright
COPY codex-release /opt/experiment-codex
COPY --chmod=0755 hook-node /opt/experiment-node/node
COPY --chmod=0755 ecc-node /usr/local/bin/node
COPY packages/*.deb /tmp/runtime-packages/
RUN dpkg -i /tmp/runtime-packages/*.deb \
 && rm -rf /tmp/runtime-packages \
 && ln -sf /opt/experiment-codex/bin/codex /usr/local/bin/codex \
 && ln -sf /opt/experiment-codex/bin/codex-code-mode-host /usr/local/bin/codex-code-mode-host \
 && printf '#!/bin/sh\nexec /opt/experiment-node/node /opt/experiment-pyright/langserver.index.js "$@"\n' > /usr/local/bin/pyright-langserver \
 && chmod 0555 /usr/local/bin/pyright-langserver \
 && test "$(codex --version)" = "codex-cli 0.163.0" \
 && test "$(node --version)" = "v24.22.1" \
 && test "$(/opt/experiment-node/node --version)" = "v24.19.0" \
 && PYTHONPATH=/opt/experiment-serena/site-packages PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
    /opt/experiment-serena/python/bin/python3 -c 'import serena, mcp; import importlib.metadata as m; assert m.version("serena-agent") == "1.6.1"; assert m.version("mcp") == "1.28.1"' \
 && python3 -c 'import numpy, scipy, Cython'
