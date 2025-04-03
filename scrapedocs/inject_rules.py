#!/usr/bin/env python3

"""
inject_rules.py

Usage:
    inject-rules my-new-app --rules shadcn tailwind prisma --run "pnpm create t3-app@latest"
    inject-rules my-new-app --rules prisma --run-script setup.sh

Description:
    - Copies local rules into a blank or scaffolded project under /docs
    - Optionally runs one or more shell commands or a script in the new project
"""

import argparse
import os
import shutil
import subprocess
from pathlib import Path


def copy_docs(topics, source_root, dest_root, verbose=False):
    dest_docs = Path(dest_root) / ".cursor/rules"
    dest_docs.mkdir(parents=True, exist_ok=True)

    for topic in topics:
        src = Path(source_root) / f"{topic}.mdc"
        dst = dest_docs / f"{topic}.mdc"

        if not src.exists():
            print(f"❌ Skipping {topic}: not found at {src}")
            continue

        if dst.exists():
            shutil.rmtree(dst)
        shutil.copyfile(src, dst)
        if verbose:
            print(f"✅ Copied {topic} to {dst}")

    print(f"✨ Rules injected into {dest_root}")


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
    parser.add_argument("--rules", nargs="+", help="Names of documentation folders to inject", default=["convex", "t3", "react-query"])
    parser.add_argument("--from", dest="source_root", default="~/Documentation/rules", help="Path to centralized docs")
    parser.add_argument("--run", nargs="+", help="Command(s) to run after injection (in project root)")
    parser.add_argument("--run-script", help="Path to a shell script to run inside the project root")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    project_path = Path(args.project).expanduser().resolve()
    source_root = Path(args.source_root).expanduser().resolve()

    copy_docs(args.rules, source_root, project_path, verbose=args.verbose)

    if args.run:
        run_commands(args.run, cwd=project_path)

    if args.run_script:
        run_script(args.run_script, cwd=project_path)


if __name__ == "__main__":
    main()
