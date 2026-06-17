import pytest
from pathlib import Path
from stages.powershell_import import check_cache_exists, parse_cache_files, import_powershell_cache

def test_check_cache_exists_true(tmp_path):
    # Create mock cache files
    scripts_dir = tmp_path / "Scripts"
    scripts_dir.mkdir()
    (scripts_dir / "fetch-summary.csv").write_text("test")
    (scripts_dir / "content-matrix.csv").write_text("test")

    exists = check_cache_exists(str(tmp_path))
    assert exists is True

def test_check_cache_exists_false(tmp_path):
    exists = check_cache_exists(str(tmp_path))
    assert exists is False

def test_parse_cache_files(tmp_path):
    scripts_dir = tmp_path / "Scripts"
    scripts_dir.mkdir()

    # Create mock fetch-summary.csv
    fetch_summary = """Agent,HTTP,HtmlBytes
Browser,200,824693
Google,200,416960"""
    (scripts_dir / "fetch-summary.csv").write_text(fetch_summary)

    # Create mock content-matrix.csv
    content_matrix = """Check,Browser,Google
HTTP 200,True,True
Product JSON-LD,True,True"""
    (scripts_dir / "content-matrix.csv").write_text(content_matrix)

    cache = parse_cache_files(str(tmp_path))

    assert "fetch_summary" in cache
    assert "content_matrix" in cache
    assert len(cache["fetch_summary"]) == 2  # 2 agents
    assert cache["fetch_summary"][0]["Agent"] == "Browser"

def test_import_powershell_cache(tmp_path):
    scripts_dir = tmp_path / "Scripts"
    scripts_dir.mkdir()

    # Create minimal cache
    (scripts_dir / "fetch-summary.csv").write_text("Agent,HTTP\nBrowser,200")
    (scripts_dir / "content-matrix.csv").write_text("Check,Browser\nHTTP 200,True")

    from core.context import AuditContext

    context = AuditContext(url="https://example.com/test")
    result = import_powershell_cache(context, str(tmp_path))

    assert result.powershell_cache is not None
    assert "fetch_summary" in result.powershell_cache

def test_import_powershell_cache_no_cache():
    from core.context import AuditContext

    context = AuditContext(url="https://example.com/test")
    result = import_powershell_cache(context, "/nonexistent")

    assert result.powershell_cache is None
