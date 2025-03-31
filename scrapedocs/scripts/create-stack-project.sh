#!/usr/bin/env bash

# create-stack-project.sh
# Interactive CLI to scaffold and inject context into a new AI-ready project

set -e

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

clear
echo -e "\033[1;36m"
echo "╭──────────────────────────────────────────────╮"
echo "│     🚀 create-stack: AI Dev Bootstrapper     │"
echo "╰──────────────────────────────────────────────╯"
echo -e "\033[0m"

T3_VERSION=""
echo "🧱 What type of project would you like to create?"
select STACK in "T3 App" "TanStack Router" "Blank Project"; do
  case $STACK in
    "T3 App")
      STACK_NAME="t3"
      echo
      read -rp "📦 Which version of create-t3-app would you like to use? (press Enter for latest): " T3_VERSION
      T3_VERSION=${T3_VERSION:-latest}
      break
      ;;
    "TanStack Router")
      STACK_NAME="tanstack"
      break
      ;;
    "Blank Project")
      STACK_NAME="blank"
      break
      ;;
    *) echo "❌ Invalid option. Please choose 1, 2, or 3.";;
  esac
done

echo "\n📁 What should the project folder be named?"
read -rp "Project name: " PROJECT_NAME
PROJECT_PATH="./$PROJECT_NAME"

echo
read -rp "📚 Where are your scraped docs stored? (press Enter to use ~/Documentation/docs-central): " SOURCE_DOCS
SOURCE_DOCS=${SOURCE_DOCS:-~/Documentation/docs-central}

echo "\n📚 Which docs do you want to inject? (space separated, e.g. shadcn tailwind prisma)"
read -rp "Docs: " DOC_LIST

# Scaffold stack
if [ "$STACK_NAME" == "t3" ]; then
  "$SCRIPT_DIR/setup-t3-app.sh" "$PROJECT_NAME" "$T3_VERSION"
elif [ "$STACK_NAME" == "tanstack" ]; then
  "$SCRIPT_DIR/setup-tanstack.sh" "$PROJECT_NAME"
else
  mkdir -p "$PROJECT_NAME"
fi

inject-context "$PROJECT_PATH" --docs $DOC_LIST --from "$SOURCE_DOCS" --verbose

echo -e "\n✅ \033[1;32mProject created at $PROJECT_PATH with injected context and stack: $STACK_NAME\033[0m\n"
