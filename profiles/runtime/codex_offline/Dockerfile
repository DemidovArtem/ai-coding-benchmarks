FROM sha256:3407cf8372c295e58722ff3ce33a0797e59e768cdaec496e20a15ef876505269

COPY codex-release /opt/codex/packages/standalone/releases/0.163.0-x86_64-unknown-linux-musl
RUN ln -s releases/0.163.0-x86_64-unknown-linux-musl /opt/codex/packages/standalone/current \
 && ln -s /opt/codex/packages/standalone/current/bin/codex /usr/local/bin/codex \
 && test "$(codex --version)" = "codex-cli 0.163.0"
