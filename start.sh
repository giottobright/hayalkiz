#!/usr/bin/env bash
set -euo pipefail

echo "==== Timeweb start.sh ===="
echo "PWD: $(pwd)"
echo "Python: $(python -V 2>/dev/null || true)"
echo "Node: $(node -v 2>/dev/null || true)"
echo "PORT: ${PORT:-unset}"
echo "HOST: ${HOST:-unset}"
echo "ENV VARS (key ones):"
env | grep -E '^(PORT|HOST|WEBHOOK_URL|WEBAPP_URL|TELEGRAM_BOT_TOKEN|OPENAI_API_KEY|DATABASE_PATH|FLUX_API_URL|FLUX_API_KEY)=' || true

echo "Listing back/ and requirements:"
ls -la back || true
echo "requirements.txt (root):"
cat requirements.txt || true

echo "Installing dependencies (root requirements.txt -> back/requirements.txt):"
pip install --no-cache-dir -r requirements.txt || pip install --no-cache-dir -r back/requirements.txt || true

echo "Launching backend: python back/start.py"
exec python back/start.py

