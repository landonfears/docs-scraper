#!/usr/bin/env python3

import os
import shutil
import argparse
from pathlib import Path

def copy_docs(topics, source_dir, target_dir, verbose=False, skip_existing=False):
    for topic in topics:
        src_path = Path(source_dir) / topic
        dst_path = Path(target_dir) / topic

        if not src_path.exists():
            print(f"❌ Source not found: {src_path}")
            continue

        if dst_path.exists():
            if skip_existing:
                print(f"⏭️ Skipping existing: {dst_path}")
                continue
            response = input(f"⚠️ {dst_path} exists. Overwrite? [y/N]: ").strip().lower()
            if response != 'y':
                print(f"🚫 Skipped: {dst_path}")
                continue
            shutil.rmtree(dst_path)

        shutil.copytree(src_path, dst_path)
        if verbose:
            print(f"✅ Copied {topic} to {dst_path}")

def main():
    parser = argparse.ArgumentParser(description="Copy scraped docs into your project for Copilot context")
    parser.add_argument("topics", nargs="+", help="Names of the doc folders to copy (e.g., shadcn tailwind prisma)")
    parser.add_argument("--from", dest="source_dir", required=True, help="Centralized docs location")
    parser.add_argument("--to", dest="target_dir", required=True, help="Destination project's /docs directory")
    parser.add_argument("--verbose", action="store_true", help="Print each copy step")
    parser.add_argument("--skip-existing", action="store_true", help="Skip folders that already exist instead of prompting")

    args = parser.parse_args()

    copy_docs(args.topics, args.source_dir, args.target_dir, verbose=args.verbose, skip_existing=args.skip_existing)

if __name__ == "__main__":
    main()