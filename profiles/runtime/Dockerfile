FROM hyd2apse/swe-milestone__burntsushi_ripgrep_14.1.1_15.0.0__base-offline@sha256:a22b225816bfc9fa243456a710bfc6e25ba6342c1162053a7876a73bfdec7e58

RUN rustup component add --toolchain 1.88.0 rust-analyzer rust-src
COPY python /opt/experiment-serena/python
COPY site-packages /opt/experiment-serena/site-packages
COPY node /opt/experiment-node/node
RUN /opt/experiment-node/node --version && /usr/local/cargo/bin/rust-analyzer --version
