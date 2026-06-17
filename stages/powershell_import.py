"""PowerShell cache import logic."""

import csv
from pathlib import Path
from typing import Any
from core.context import AuditContext


def check_cache_exists(base_path: str) -> bool:
    """Check if PowerShell cache files exist."""
    scripts_dir = Path(base_path) / "Scripts"

    if not scripts_dir.exists():
        return False

    required_files = ["fetch-summary.csv", "content-matrix.csv"]

    for filename in required_files:
        if not (scripts_dir / filename).exists():
            return False

    return True


def parse_cache_files(base_path: str) -> dict[str, Any]:
    """Parse PowerShell cache CSV files."""
    scripts_dir = Path(base_path) / "Scripts"
    cache = {}

    # Parse fetch-summary.csv
    fetch_summary_path = scripts_dir / "fetch-summary.csv"
    if fetch_summary_path.exists():
        with fetch_summary_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            cache["fetch_summary"] = list(reader)

    # Parse content-matrix.csv
    content_matrix_path = scripts_dir / "content-matrix.csv"
    if content_matrix_path.exists():
        with content_matrix_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            cache["content_matrix"] = list(reader)

    # Parse coverage-summary.csv if exists
    coverage_summary_path = scripts_dir / "coverage-summary.csv"
    if coverage_summary_path.exists():
        with coverage_summary_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            cache["coverage_summary"] = list(reader)

    return cache


def import_powershell_cache(context: AuditContext, base_path: str) -> AuditContext:
    """Import PowerShell cache into audit context."""
    if not check_cache_exists(base_path):
        context.powershell_cache = None
        return context

    cache = parse_cache_files(base_path)
    context.powershell_cache = cache

    return context
