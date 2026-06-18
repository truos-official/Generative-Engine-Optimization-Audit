import pytest
from stages.prompts import (
    generate_reference_facts, extract_characteristics,
    build_unbranded_query, build_unbranded_prompts
)
from core.context import ProductSchema

def test_generate_reference_facts():
    schema_dict = {
        "product_id": "TEST-001",
        "name": "Test Product",
        "price": "99.99",
        "currency": "USD"
    }

    facts = generate_reference_facts(schema_dict, [], "chemical_reagent")

    assert facts["core"]["product_id"] == "TEST-001"
    assert "chemical" in facts
    assert "commercial" in facts

def test_extract_characteristics():
    facts = {
        "core": {"product_name": "Test Medium"},
        "culture": {}
    }

    characteristics = extract_characteristics(facts, "cell_culture_media")

    assert "application" in characteristics
    assert "product_type" in characteristics

def test_build_unbranded_query():
    characteristics = {
        "product_type": "culture medium",
        "application": "cell culture"
    }

    query = build_unbranded_query(characteristics, "specificity")

    assert "culture medium" in query
    assert "cell culture" in query
    assert query.endswith("?")

def test_build_unbranded_prompts():
    facts = {
        "core": {"product_name": "Test"},
        "culture": {}
    }

    prompts = build_unbranded_prompts(facts, [], "cell_culture_media", 70)

    assert len(prompts) == 6  # 6 dimensions
    assert all(p.dimension in ["specificity", "entity_understanding", "workflow_understanding",
                                 "evidence_trust", "comparison", "commercial"] for p in prompts)
    assert all(p.pass_threshold == 70 for p in prompts)
