#!/usr/bin/env bash

# setup-t3-app.sh
# Scaffolds a new T3 App using pnpm create and installs dependencies

set -e  # Exit on any error

APP_NAME=${1:-t3-app}

echo "🧱 Scaffolding T3 app in folder: $APP_NAME"

T3_VERSION=${2:-latest}
pnpm create "t3-app@$T3_VERSION" "$APP_NAME"
cd "$APP_NAME"

echo "📦 Installing dependencies with pnpm"
pnpm install

echo "✅ T3 App setup complete in: $APP_NAME"

# Optionally launch in Cursor
if command -v cursor &> /dev/null; then
  echo "🚀 Launching in Cursor..."
  cursor .
fi
