#!/usr/bin/env bash
set -euo pipefail

# 1. Warn if running on a Windows mount
if [[ "$PWD" == /mnt/* ]]; then
  echo "⚠️  You’re in a Windows-mounted folder."
  echo "    It’s strongly recommended to move this project into your Linux home:"
  echo "    mv \"$PWD\" \"$HOME/$(basename "$PWD")\""
  echo
fi

# 2. Fix ownership & permissions
echo "🛠  Fixing permissions…"
sudo chown -R "$(id -u):$(id -g)" .
chmod -R u+rwX .

# 3. Remove any old venv
echo "🧹  Cleaning up old virtualenv…"
rm -rf .venv

# 4. Create a fresh virtual environment
echo "🐍  Creating new venv…"
uv venv mlops

# 5. Activate venv
echo "⚡️  Activating venv…"
# shellcheck disable=SC1091
source mlops/bin/activate

# 6. Upgrade installer tools via uv
echo "⬆️  Upgrading pip & wheel via uv…"
uv pip install --upgrade pip wheel

# 7. Install requirements via uv
echo "📦  Installing requirements.txt via uv…"
uv pip install -r requirements.txt

echo
echo "✅  Setup complete. Your venv is in .venv, activate with:"
echo "    source mlops/bin/activate"
