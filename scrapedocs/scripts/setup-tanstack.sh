#!/usr/bin/env bash

# setup-tanstack.sh
# Example bootstrapping script for a TanStack Router + React starter

set -e  # Exit on error

APP_NAME=${1:-start-basic}

echo "📦 Cloning TanStack starter into: $APP_NAME"
npx gitpick TanStack/router/tree/main/examples/react/start-basic "$APP_NAME"
cd "$APP_NAME"

echo "📦 Installing dependencies with pnpm"
pnpm install

echo "✅ TanStack example is ready in: $APP_NAME"

# Optionally open in Cursor
if command -v cursor &> /dev/null; then
  echo "🚀 Launching in Cursor..."
  cursor .
fi
