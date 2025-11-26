FROM rust:latest

# Install wasm-pack
RUN curl https://rustwasm.github.io/wasm-pack/installer/init.sh -sSf | sh

WORKDIR /app

# Copy the build script
COPY build_wasm.sh /usr/local/bin/build_wasm.sh
RUN chmod +x /usr/local/bin/build_wasm.sh

ENTRYPOINT ["build_wasm.sh"]
