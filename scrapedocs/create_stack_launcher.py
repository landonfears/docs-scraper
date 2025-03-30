# create_stack_launcher.py
# Python launcher to wrap the Bash CLI from pyproject.toml

import subprocess
import os
import sys
from pathlib import Path

def main():
    script_path = Path(__file__).parent / "scripts" / "create-stack-project.sh"

    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return

    # Handle built-in flags
    if "--help" in sys.argv:
        print("\nUsage: create-stack [--help] [--version]\n")
        print("Launch an interactive CLI to scaffold a dev project with local doc injection.")
        return

    if "--version" in sys.argv:
        print("create-stack version 0.2.0")
        return

    subprocess.run(["bash", str(script_path), *sys.argv[1:]], check=True)