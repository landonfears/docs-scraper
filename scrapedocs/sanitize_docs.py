import os
import re
import click
from pathlib import Path

@click.command()
@click.option('--path', '-p', required=True, type=click.Path(exists=True, file_okay=False), help='Directory to scan for .md files')
@click.option('--dry-run', is_flag=True, default=False, help='Preview changes without overwriting files')
@click.option('--verbose', is_flag=True, default=False, help='Show cleaned files and line removals')
def sanitize_docs(path, dry_run, verbose):
    """Smart sanitizer: removes embedded JS/CSS and junk from markdown files."""
    md_files = Path(path).rglob("*.md")
    cleaned = 0

    def is_garbage_line(line):
        if len(line) > 200:
            return True
        if re.search(r"!function|window\.|document\.|:where\\|--", line):
            return True
        non_alpha_ratio = len(re.findall(r"[^\w\s]", line)) / max(len(line), 1)
        return non_alpha_ratio > 0.5

    for file in md_files:
        lines = file.read_text(encoding='utf-8').splitlines()
        original = lines[:]
        cleaned_lines = []

        for line in lines:
            if is_garbage_line(line):
                if verbose:
                    click.echo(f"🗑 Removed: {line[:80]}... from {file.name}")
                continue
            cleaned_lines.append(line)

        cleaned_text = "\n".join(cleaned_lines).strip()

        if cleaned_text != "\n".join(original).strip():
            if not dry_run:
                file.write_text(cleaned_text + "\n", encoding='utf-8')
            cleaned += 1

    click.echo(f"✅ Sanitized {cleaned} markdown file(s) in {path}{' (dry-run)' if dry_run else ''}")

if __name__ == '__main__':
    sanitize_docs()
