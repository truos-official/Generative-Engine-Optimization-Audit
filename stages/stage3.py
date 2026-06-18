"""Stage 3: Extract & Classify orchestrator."""

from core.context import AuditContext
from stages.extract import extract_json_ld, find_product_schema, parse_product_schema, extract_content_blocks, build_visibility_matrix
from stages.classify import classify_product_category, calculate_crawler_coverage


def run_stage3(context: AuditContext, config: dict) -> AuditContext:
    """Stage 3: Extract content, classify, and score coverage."""

    # Get browser HTML for extraction
    browser_html = context.http_responses.get("browser", {}).get("html", "")

    if not browser_html:
        return context

    # Extract JSON-LD and find product schema
    json_ld_blocks = extract_json_ld(browser_html)
    product_schema_dict = find_product_schema(json_ld_blocks)

    if product_schema_dict:
        context.product_schema = parse_product_schema(product_schema_dict)
        context.product_id = context.product_schema.product_id

    # Extract content blocks
    context.content_blocks = extract_content_blocks(browser_html, context.url)

    # Build visibility matrix
    context.visibility_matrix = build_visibility_matrix(
        context.content_blocks,
        context.http_responses
    )

    # Classify product category
    if context.product_schema:
        category, confidence = classify_product_category(
            context.product_schema.name or "",
            context.product_schema.description or ""
        )
        context.product_category = category

    # Calculate crawler coverage scores
    weights = config.get("content_extraction", {}).get("weights", {})
    context.crawler_coverage_scores = calculate_crawler_coverage(
        context.visibility_matrix,
        context.content_blocks,
        weights
    )

    return context
