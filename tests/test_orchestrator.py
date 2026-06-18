"""Tests for main orchestrator."""

import pytest
from pathlib import Path
from core.orchestrator import run_audit
from core.config import load_config


@pytest.mark.asyncio
async def test_run_audit_basic():
    """Test basic audit execution."""

    # Load config
    config = load_config("config.yaml")

    # Create temp output dir
    output_dir = "test_outputs"
    Path(output_dir).mkdir(exist_ok=True)

    # Run audit (with simple URL)
    url = "https://www.thermofisher.com/order/catalog/product/C-22010"

    context = await run_audit(url, config, output_dir)

    # Check context populated
    assert context.url == url
    assert context.overall_score >= 0
    assert context.geo_risk_level in ["low", "medium", "high", "critical", "unknown"]

    # Check output files
    assert "audit_json" in context.output_files
    audit_json_path = Path(context.output_files["audit_json"])
    assert audit_json_path.exists()

    # Cleanup
    if audit_json_path.exists():
        audit_json_path.unlink()
