"""Stage 5: Gap Diagnosis & Remediation."""

from core.context import AuditContext, GapEntry, RemediationItem, RootCause


def diagnose_gaps(context: AuditContext) -> list[GapEntry]:
    """Diagnose gaps from failing agent results."""
    gaps = []

    for result in context.agent_results:
        # Check if failed (score below threshold)
        if result.live_score < 70:
            # Determine failure type
            failure_type = "low_score"

            if result.retrieval_analysis and not result.retrieval_analysis.retrieved_target:
                failure_type = "retrieval_failure"

            # Create root cause
            root_cause = RootCause(
                type="retrieval_failure" if failure_type == "retrieval_failure" else "content_gap",
                layer="search" if failure_type == "retrieval_failure" else "server-rendered",
                missing_content=[],
                contributing_factors=[failure_type]
            )

            # Map to fix category
            fix_category = "infrastructure_gap" if failure_type == "retrieval_failure" else "content_gap"

            gap = GapEntry(
                dimension=result.dimension,
                agent=f"{result.agent_name}/{result.model_name}",
                failure_type=failure_type,
                root_cause=root_cause,
                fix_category=fix_category,
                evidence_ids=[],
                explanation=f"Score {result.live_score} below threshold",
                geo_impact="medium"
            )

            gaps.append(gap)

    return gaps


def prioritize_remediations(gaps: list[GapEntry]) -> list[RemediationItem]:
    """Prioritize remediations by impact."""
    # Group by fix category
    by_category = {}
    for gap in gaps:
        if gap.fix_category not in by_category:
            by_category[gap.fix_category] = []
        by_category[gap.fix_category].append(gap)

    remediations = []

    for category, category_gaps in by_category.items():
        dimensions = list(set(g.dimension for g in category_gaps))
        agents = list(set(g.agent for g in category_gaps))

        # Estimate effort
        effort = "small" if len(category_gaps) < 3 else "medium" if len(category_gaps) < 7 else "large"

        # Calculate impact
        impact_score = len(category_gaps) * len(dimensions) * 10

        remediation = RemediationItem(
            fix_category=category,
            owner="webmaster" if "infrastructure" in category else "content_team",
            gaps_addressed=len(category_gaps),
            dimensions_affected=dimensions,
            agents_affected=agents,
            effort_estimate=effort,
            impact_score=float(impact_score),
            priority_rank=0,
            specific_actions=[],
            retest_condition="Re-audit after fixes",
            evidence_ids=[]
        )

        remediations.append(remediation)

    # Sort by impact
    remediations.sort(key=lambda r: r.impact_score, reverse=True)

    # Assign ranks
    for i, rem in enumerate(remediations):
        rem.priority_rank = i + 1

    return remediations


def calculate_overall_score(context: AuditContext) -> tuple[float, str]:
    """Calculate overall score and risk level."""
    if not context.agent_results:
        return 0.0, "unknown"

    # Average all live scores
    total_score = sum(r.live_score for r in context.agent_results)
    avg_score = total_score / len(context.agent_results)

    # Determine risk level
    if avg_score >= 90:
        risk_level = "low"
    elif avg_score >= 75:
        risk_level = "medium"
    elif avg_score >= 50:
        risk_level = "high"
    else:
        risk_level = "critical"

    return round(avg_score, 1), risk_level


def run_stage5(context: AuditContext, config: dict) -> AuditContext:
    """Stage 5: Diagnose gaps and generate remediations."""

    # Diagnose gaps
    context.gaps = diagnose_gaps(context)

    # Prioritize remediations
    context.remediations = prioritize_remediations(context.gaps)

    # Calculate overall score
    context.overall_score, context.geo_risk_level = calculate_overall_score(context)

    return context
