#!/usr/bin/env python3

"""
inject_context.py

Usage:
    inject-context my-new-app --docs shadcn tailwind prisma --run "pnpm create t3-app@latest"
    inject-context my-new-app --docs prisma --run-script setup.sh

Description:
    - Copies local docs into a blank or scaffolded project under /docs
    - Injects an onboarding README so Cursor AI understands the docs
    - Adds a .cursor/config.json file to guide Cursor context awareness
    - Optionally runs one or more shell commands or a script in the new project
"""

import argparse
import os
import shutil
import subprocess
from pathlib import Path

TEMPLATE_ONBOARDING = Path(__file__).parent / "Cursor-Onboarding-Guide.md"
CURSOR_CONFIG = Path(__file__).parent / "cursor_config.json"


def copy_docs(topics, source_root, dest_root, verbose=False):
    dest_docs = Path(dest_root) / "docs"
    dest_docs.mkdir(parents=True, exist_ok=True)

    for topic in topics:
        src = Path(source_root) / topic
        dst = dest_docs / topic

        if not src.exists():
            print(f"❌ Skipping {topic}: not found at {src}")
            continue

        if dst.exists():
            shutil.rmtree(dst)
        dst.symlink_to(src, target_is_directory=True)
        if verbose:
            print(f"✅ Copied {topic} to {dst}")

    # Copy the onboarding guide
    onboarding_dst = Path(dest_root) / "docs" / "README.md"
    shutil.copyfile(TEMPLATE_ONBOARDING, onboarding_dst)
    if verbose:
        print(f"📘 Injected Cursor onboarding guide → {onboarding_dst}")

    # Copy .cursor config
    cursor_dst = Path(dest_root) / ".cursor" / "config.json"
    cursor_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(CURSOR_CONFIG, cursor_dst)
    if verbose:
        print(f"⚙️  Injected Cursor config → {cursor_dst}")

    print(f"✨ Docs and context injected into {dest_root}")


def run_commands(commands, cwd):
    if isinstance(commands, str):
        commands = [commands]

    for cmd in commands:
        print(f"▶️ Running: {cmd}")
        subprocess.run(cmd, shell=True, cwd=cwd, check=True)


def run_script(script_path, cwd):
    script = Path(script_path).expanduser().resolve()
    if not script.exists():
        raise FileNotFoundError(f"Script not found: {script}")

    print(f"▶️ Running script: {script}")
    subprocess.run(["bash", str(script)], cwd=cwd, check=True)


def main():
    parser = argparse.ArgumentParser(description="Inject docs + onboarding into a new AI project")
    parser.add_argument("project", help="Path to your new project root (even if blank)")
    parser.add_argument("--docs", nargs="+", required=True, help="Names of documentation folders to inject")
    parser.add_argument("--from", dest="source_root", default="~/Documentation/docs-central", help="Path to centralized docs")
    parser.add_argument("--run", nargs="+", help="Command(s) to run after injection (in project root)")
    parser.add_argument("--run-script", help="Path to a shell script to run inside the project root")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    project_path = Path(args.project).expanduser().resolve()
    source_root = Path(args.source_root).expanduser().resolve()

    copy_docs(args.docs, source_root, project_path, verbose=args.verbose)

    if args.run:
        run_commands(args.run, cwd=project_path)

    if args.run_script:
        run_script(args.run_script, cwd=project_path)


if __name__ == "__main__":
    main()
