"""
organizer.py - Collect files from a source (recursively) and organize them
               by extension into a chosen destination directory.

Usage:
    python organizer.py --src SOURCE_DIR --dest DEST_DIR [--dry-run]

    --src   Directory to scan recursively for files.
    --dest  Directory where extension folders will be created.
    --dry-run  Preview changes without moving anything.
"""

import argparse
import shutil
from pathlib import Path


def collect_files(src: Path) -> list[Path]:
    """Return all files under src, recursively, skipping the dest if nested."""
    return [f for f in src.rglob("*") if f.is_file()]


def unique_dest(dest_dir: Path, filename: str) -> Path:
    """Return a collision-free path inside dest_dir for the given filename."""
    candidate = dest_dir / filename
    if not candidate.exists():
        return candidate
    stem, suffix = Path(filename).stem, Path(filename).suffix
    counter = 1
    while True:
        candidate = dest_dir / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def organize(src: Path, dest: Path, dry_run: bool = False) -> None:
    files = collect_files(src)

    if not files:
        print("No files found.")
        return

    moved = 0

    for file in files:
        # Skip files that already live inside dest (avoid moving dest into itself)
        try:
            file.relative_to(dest)
            continue
        except ValueError:
            pass

        ext = file.suffix.lstrip(".").lower() or "no_extension"
        ext_dir = dest / ext
        target = unique_dest(ext_dir, file.name)

        rel = file.relative_to(src)
        if dry_run:
            print(f"[dry-run] {rel}  ->  {ext}/{target.name}")
        else:
            ext_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file), target)
            print(f"Moved: {rel}  ->  {ext}/{target.name}")
            moved += 1

    if not dry_run:
        print(f"\nDone. {moved} file(s) moved.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Organize files from SOURCE into DEST, grouped by extension."
    )
    parser.add_argument("--src", required=True, help="Directory to scan recursively")
    parser.add_argument(
        "--dest", required=True, help="Directory where extension folders are created"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without moving any files",
    )
    args = parser.parse_args()

    src = Path(args.src).resolve()
    dest = Path(args.dest).resolve()

    for path, label in ((src, "source"), (dest, "destination")):
        if not path.exists():
            print(f"Error: {label} directory '{path}' does not exist.")
            raise SystemExit(1)
        if not path.is_dir():
            print(f"Error: '{path}' is not a directory.")
            raise SystemExit(1)

    organize(src, dest, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
