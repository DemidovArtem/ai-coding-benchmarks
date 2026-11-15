FROM hyd2apse/swe-milestone__burntsushi_ripgrep_14.1.1_15.0.0__base-offline@sha256:a22b225816bfc9fa243456a710bfc6e25ba6342c1162053a7876a73bfdec7e58

COPY codex-release /opt/codex-release
COPY --chmod=0755 node /usr/local/bin/node
RUN ln -s /opt/codex-release/bin/codex /usr/local/bin/codex \
 && ln -s /opt/codex-release/bin/codex-code-mode-host /usr/local/bin/codex-code-mode-host \
 && test "$(codex --version)" = "codex-cli 0.163.0" \
 && node --version
