# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal Python utility project ("miscelaneo para mi vida diaria"). The `reorg/` module is a file organization tool currently under active development on the `feature/org` branch.

## Development Setup

No package manager config exists yet. Set up a virtual environment manually:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt  # once the file is created
```

## Common Commands

Once tooling is configured, the expected stack (per `.gitignore`) is:

| Task | Command |
|------|---------|
| Lint | `ruff check .` |
| Format | `ruff format .` |
| Type check | `mypy .` |
| Run tests | `pytest` |
| Run single test | `pytest path/to/test_file.py::test_name` |

## Architecture

```
reorg/
  organizer.py   # Entry point for the file-organization feature
```

The `.gitignore` also accounts for:
- **LaTeX** workflows (thesis/research documents compiled with `latexmk`)
- **Data files** under `data/` (CSV/XLSX) — these are intentionally ignored from version control
- **Jupyter / Marimo** notebooks for exploratory analysis
- **Abstra** automation framework
