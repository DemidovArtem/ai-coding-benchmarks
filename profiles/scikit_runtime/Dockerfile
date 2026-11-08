FROM sha256:3407cf8372c295e58722ff3ce33a0797e59e768cdaec496e20a15ef876505269 AS semantic
FROM sha256:81d26906645667f05184d2477d0891aae18b05fb9e1bf5375b378ac2e2fa7fb2 AS codex
FROM hyd2apse/swe-milestone__scikit-learn_scikit-learn_1.5.2_1.6.0__base-offline@sha256:2b77ce7d7030461e3e7ca67e47d910d7fa0e6784c7520c62f183ebcde837bd0a

COPY --from=semantic /opt/experiment-serena /opt/experiment-serena
COPY --from=semantic /opt/experiment-node /opt/experiment-node
COPY --from=codex /opt/codex/packages/standalone/releases/0.163.0-x86_64-unknown-linux-musl /opt/experiment-codex
COPY pyright /opt/experiment-pyright
RUN apt-get update \
 && apt-get install -y --no-install-recommends sudo iptables \
 && rm -rf /var/lib/apt/lists/* \
 && ln -sf /opt/experiment-codex/bin/codex /usr/local/bin/codex \
 && ln -sf /opt/experiment-node/node /usr/local/bin/node \
 && printf '#!/bin/sh\nexec /opt/experiment-node/node /opt/experiment-pyright/langserver.index.js "$@"\n' > /usr/local/bin/pyright-langserver \
 && chmod 0555 /usr/local/bin/pyright-langserver \
 && test "$(codex --version)" = "codex-cli 0.163.0" \
 && python3 -c 'import numpy, scipy, Cython; print(numpy.__version__, scipy.__version__, Cython.__version__)'
