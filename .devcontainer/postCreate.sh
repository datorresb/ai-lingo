#!/bin/bash
set -e

# Configure GitHub credentials if provided
if [ -n "${GITHUB_USER:-}" ] && [ -n "${GITHUB_TOKEN:-}" ]; then
  echo "Configuring GitHub credentials..."
  printf 'https://%s:%s@github.com\n' "$GITHUB_USER" "$GITHUB_TOKEN" >> "$HOME/.git-credentials"
  chmod 600 "$HOME/.git-credentials" || true

  echo "Configuring git credential helper (store)"
  git config --global credential.helper store
  git config --global credential.useHttpPath true
fi

# Install Claude Code CLI (optional)
if [ "${INSTALL_CLAUDE:-false}" = "true" ]; then
  echo "Installing Claude Code CLI..."
  curl -fsSL https://claude.ai/install.sh | bash || echo "Claude CLI installation failed (non-blocking)"
else
  echo "Skipping Claude CLI (set INSTALL_CLAUDE=true to enable)"
fi

# Install Azure CLI (optional)
if [ "${INSTALL_AZURE_CLI:-false}" = "true" ]; then
  echo "Installing Azure CLI..."
  curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash || echo "Azure CLI installation failed (non-blocking)"
else
  echo "Skipping Azure CLI (set INSTALL_AZURE_CLI=true to enable)"
fi

echo "postCreate done"