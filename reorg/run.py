"""
run.py - Interactive launcher for the file organizer.

Just run:  python reorg/run.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from organizer import organize

HOME = Path.home()

COMMON_PATHS = {
    "1": ("Downloads",  HOME / "Downloads"),
    "2": ("Desktop",    HOME / "Desktop"),
    "3": ("Documents",  HOME / "Documents"),
    "4": ("Pictures",   HOME / "Pictures"),
    "5": ("Music",      HOME / "Music"),
    "6": ("Videos",     HOME / "Videos"),
}


def pick_directory(prompt: str) -> Path:
    print(f"\n{prompt}")
    print("-" * 40)
    for key, (label, path) in COMMON_PATHS.items():
        exists = "" if path.exists() else "  (not found)"
        print(f"  {key}) {label:<12} {path}{exists}")
    print("  0) Enter a custom path")
    print("-" * 40)

    while True:
        choice = input("Your choice: ").strip()

        if choice in COMMON_PATHS:
            _, path = COMMON_PATHS[choice]
            if not path.exists():
                print(f"  That folder doesn't exist on this machine. Try another.")
                continue
            return path

        if choice == "0":
            while True:
                raw = input("  Paste the full path: ").strip().strip('"')
                path = Path(raw).expanduser().resolve()
                if path.is_dir():
                    return path
                print(f"  '{raw}' is not a valid directory. Try again.")

        print("  Invalid option. Please enter a number from the list.")


def main() -> None:
    print("=" * 40)
    print("       FILE ORGANIZER")
    print("=" * 40)

    src  = pick_directory("Where do you want to organize FROM?")
    dest = pick_directory("Where do you want to put the organized files?")

    print(f"\n  Source : {src}")
    print(f"  Dest   : {dest}")

    preview = input("\nDo a preview first? (recommended) [Y/n]: ").strip().lower()
    if preview != "n":
        print("\n--- PREVIEW (nothing will be moved) ---")
        organize(src, dest, dry_run=True)
        confirm = input("\nLooks good? Proceed with moving? [y/N]: ").strip().lower()
        if confirm != "y":
            print("Cancelled. Nothing was moved.")
            return

    print("\n--- ORGANIZING ---")
    organize(src, dest)


if __name__ == "__main__":
    main()
