"""
organizer.py - Organize files in a directory by their extension.

Usage:
    python organizer.py [TARGET_DIR] [--dry-run]

    TARGET_DIR  Directory to organize (defaults to current directory).
    --dry-run   Print what would happen without moving anything.
"""

import argparse
import shutil
from pathlib import Path


def organize(target: Path, dry_run: bool = False) -> None:
    moved = 0
    skipped = 0

    files = [f for f in target.iterdir() if f.is_file()]

    for file in files:
        ext = file.suffix.lstrip(".").lower() or "no_extension"
        dest_dir = target / ext

        if not dry_run:
            dest_dir.mkdir(exist_ok=True)

        dest = dest_dir / file.name

        if dry_run:
            print(f"[dry-run] {file.name}  ->  {ext}/{file.name}")
        else:
            shutil.move(str(file), dest)
            print(f"Moved: {file.name}  ->  {ext}/{file.name}")
            moved += 1

    if not dry_run:
        print(f"\nDone. {moved} file(s) moved, {skipped} skipped.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Organize files in a directory by extension."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Directory to organize (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without moving any files",
    )
    args = parser.parse_args()

    target = Path(args.target).resolve()
    if not target.is_dir():
        print(f"Error: '{target}' is not a valid directory.")
        raise SystemExit(1)

    organize(target, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
