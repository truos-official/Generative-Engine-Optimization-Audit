"""Reference facts and prompt generation."""

import uuid
import yaml
from pathlib import Path
from core.context import PromptExecution, SiblingProduct


def generate_reference_facts(
    product_schema: dict,
    content_blocks: list,
    category: str
) -> dict:
    """Generate reference facts from product data."""
    facts = {
        "core": {
            "product_id": product_schema.get("product_id"),
            "product_name": product_schema.get("name"),
            "canonical_url": ""
        }
    }

    # Category-specific facts
    if category == "cell_culture_media":
        facts["culture"] = {
            "storage_temp": None,
            "sterility": None,
            "supplements": []
        }
    elif category == "chemical_reagent":
        facts["chemical"] = {
            "molecular_weight": None,
            "cas_number": None,
            "purity": None
        }

    # Commercial facts
    if product_schema.get("price"):
        facts["commercial"] = {
            "price": product_schema.get("price"),
            "currency": product_schema.get("currency"),
            "availability": product_schema.get("availability")
        }

    return facts


def extract_characteristics(reference_facts: dict, category: str) -> dict:
    """Extract product characteristics for unbranded query construction."""
    characteristics = {}

    if category == "cell_culture_media":
        culture = reference_facts.get("culture", {})
        characteristics["application"] = "cell culture"
        characteristics["product_type"] = "culture medium"
    elif category == "chemical_reagent":
        characteristics["application"] = "laboratory research"
        characteristics["product_type"] = "chemical reagent"
    else:
        characteristics["application"] = "laboratory use"
        characteristics["product_type"] = "product"

    return characteristics


def build_unbranded_query(characteristics: dict, dimension: str) -> str:
    """Build generic query from characteristics."""
    product_type = characteristics.get("product_type", "product")
    application = characteristics.get("application", "research")

    if dimension == "specificity":
        return f"What makes a good {product_type} for {application}?"
    elif dimension == "entity_understanding":
        return f"I need {product_type} for {application}. What are my options?"
    elif dimension == "workflow_understanding":
        return f"I'm planning to use {product_type} for {application}. What should I know?"
    elif dimension == "evidence_trust":
        return f"What are the key factors when choosing {product_type}?"
    elif dimension == "comparison":
        return f"Compare options for {product_type}."
    elif dimension == "commercial":
        return f"Where can I buy {product_type} for {application}?"

    return ""


def build_unbranded_prompts(
    reference_facts: dict,
    siblings: list[SiblingProduct],
    category: str,
    pass_threshold: int = 70
) -> list[PromptExecution]:
    """Build unbranded prompts for all dimensions."""
    prompts = []

    characteristics = extract_characteristics(reference_facts, category)

    dimensions = [
        "specificity",
        "entity_understanding",
        "workflow_understanding",
        "evidence_trust",
        "comparison",
        "commercial"
    ]

    for dim in dimensions:
        query = build_unbranded_query(characteristics, dim)

        prompts.append(PromptExecution(
            id=f"prompt-{uuid.uuid4().hex[:8]}",
            dimension=dim,
            question=query,
            prompt=query,
            reference_content=reference_facts,
            sibling_context=siblings if dim == "entity_understanding" else None,
            pass_threshold=pass_threshold
        ))

    return prompts
