# See here for image contents: https://github.com/devcontainers/images/tree/main/src/python
ARG VARIANT="3.13-bookworm"
FROM mcr.microsoft.com/devcontainers/python:1-${VARIANT}

USER root
RUN pip install --no-cache-dir uv \
    && uv --version
USER vscode