"""Bridle CLI entry point — dev-friendly with absolute imports.

All app construction lives in main.py (single source of truth).
This module is a thin wrapper for ``pyproject.toml`` entry points.
"""

from __future__ import annotations

from harness_cli.main import app, main  # noqa: F401 — re-export for entry_points

if __name__ == "__main__":
    main()
