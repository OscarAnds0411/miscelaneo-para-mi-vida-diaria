# miscelaneo-para-mi-vida-diaria

Personal Python utilities for everyday tasks.

---

## reorg — File Organizer

Scans a source directory recursively and moves every file into extension-named folders inside a destination directory of your choice.

### Quick start (interactive)

```bash
python reorg/run.py
```

The script asks you step by step: where to organize from, where to put the result, and shows a preview before moving anything.

### Command-line usage

```bash
python reorg/organizer.py --src SOURCE_DIR --dest DEST_DIR [--dry-run]
```

| Argument | Description |
|----------|-------------|
| `--src`  | Directory to scan (all subdirectories are included) |
| `--dest` | Directory where the extension folders will be created |
| `--dry-run` | Preview what would be moved without touching any files |

### Example

```bash
# Preview
python reorg/organizer.py --src ~/Downloads --dest ~/Organized --dry-run

# Run
python reorg/organizer.py --src ~/Downloads --dest ~/Organized
```

**Before:**
```
Downloads/
  report.pdf
  photo.jpg
  docs/
    notes.pdf
    budget.xlsx
```

**After (`~/Organized`):**
```
Organized/
  pdf/
    report.pdf
    notes.pdf
  jpg/
    photo.jpg
  xlsx/
    budget.xlsx
```

Files without an extension go into `no_extension/`. If two files share the same name, the second one is renamed automatically (`file_1.pdf`, `file_2.pdf`, …).
