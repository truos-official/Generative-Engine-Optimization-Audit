"""HTML report generator."""

from pathlib import Path
from core.context import AuditContext


def generate_html_report(context: AuditContext, output_path: str) -> str:
    """Generate HTML report from audit context."""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GEO Audit Report - {context.product_id or 'Unknown'}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .score {{
            font-size: 48px;
            font-weight: bold;
            color: {'#22c55e' if context.overall_score >= 90 else '#f59e0b' if context.overall_score >= 75 else '#ef4444'};
        }}
        .risk-badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 4px;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 12px;
            background: {'#dcfce7' if context.geo_risk_level == 'low' else '#fef3c7' if context.geo_risk_level == 'medium' else '#fee2e2'};
            color: {'#166534' if context.geo_risk_level == 'low' else '#92400e' if context.geo_risk_level == 'medium' else '#991b1b'};
        }}
        .section {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h2 {{
            margin-top: 0;
            color: #1f2937;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th {{
            background: #f9fafb;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #e5e7eb;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #e5e7eb;
        }}
        .score-cell {{
            font-weight: 600;
            font-size: 16px;
        }}
        .score-good {{ color: #22c55e; }}
        .score-ok {{ color: #f59e0b; }}
        .score-bad {{ color: #ef4444; }}
        .remediation {{
            margin: 15px 0;
            padding: 15px;
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            border-radius: 4px;
        }}
        .remediation-title {{
            font-weight: 600;
            margin-bottom: 8px;
        }}
        .url {{
            font-family: 'Courier New', monospace;
            font-size: 14px;
            color: #6b7280;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>GEO Audit Report</h1>
        <div class="url">{context.url}</div>
        <div style="margin: 20px 0;">
            <span class="score">{context.overall_score}</span>
            <span style="font-size: 20px; color: #6b7280;"> / 100</span>
        </div>
        <div>
            <span class="risk-badge">{context.geo_risk_level} risk</span>
            <span style="margin-left: 15px; color: #6b7280;">
                Product: {context.product_id or 'Unknown'} |
                Category: {context.product_category or 'Unknown'}
            </span>
        </div>
    </div>

    <div class="section">
        <h2>Agent Test Results</h2>
        <table>
            <thead>
                <tr>
                    <th>Agent</th>
                    <th>Model</th>
                    <th>Dimension</th>
                    <th>Training Score</th>
                    <th>Live Score</th>
                    <th>Improvement</th>
                    <th>Traffic Verdict</th>
                </tr>
            </thead>
            <tbody>
"""

    # Add agent results
    for result in context.agent_results:
        score_class = 'score-good' if result.live_score >= 90 else 'score-ok' if result.live_score >= 75 else 'score-bad'
        improvement = result.improvement_from_live
        improvement_sign = '+' if improvement > 0 else ''

        traffic_verdict = result.traffic_analysis.traffic_verdict if result.traffic_analysis else 'unknown'

        html += f"""
                <tr>
                    <td>{result.agent_name}</td>
                    <td>{result.model_name}</td>
                    <td>{result.dimension}</td>
                    <td class="score-cell">{result.training_score:.1f}</td>
                    <td class="score-cell {score_class}">{result.live_score:.1f}</td>
                    <td>{improvement_sign}{improvement:.1f}</td>
                    <td>{traffic_verdict}</td>
                </tr>
"""

    html += """
            </tbody>
        </table>
    </div>
"""

    # Add remediations
    if context.remediations:
        html += """
    <div class="section">
        <h2>Recommended Remediations</h2>
"""
        for rem in context.remediations[:5]:  # Top 5
            html += f"""
        <div class="remediation">
            <div class="remediation-title">#{rem.priority_rank}: {rem.fix_category.replace('_', ' ').title()}</div>
            <div style="color: #6b7280; margin-top: 5px;">
                Addresses {rem.gaps_addressed} gaps |
                Impact: {rem.impact_score:.0f} |
                Effort: {rem.effort_estimate} |
                Owner: {rem.owner}
            </div>
            <div style="margin-top: 8px;">
                Dimensions: {', '.join(rem.dimensions_affected)}
            </div>
        </div>
"""
        html += """
    </div>
"""

    # Add coverage scores
    if context.crawler_coverage_scores:
        html += """
    <div class="section">
        <h2>Crawler Coverage Scores</h2>
        <table>
            <thead>
                <tr>
                    <th>Agent</th>
                    <th>Coverage Score</th>
                </tr>
            </thead>
            <tbody>
"""
        for agent, score in context.crawler_coverage_scores.items():
            html += f"""
                <tr>
                    <td>{agent}</td>
                    <td class="score-cell">{score:.1f}%</td>
                </tr>
"""
        html += """
            </tbody>
        </table>
    </div>
"""

    html += """
    <div class="section" style="text-align: center; color: #6b7280; font-size: 14px;">
        Generated by eCommerce GEO Auditor
    </div>
</body>
</html>
"""

    # Write file
    output_file = Path(output_path)
    output_file.write_text(html, encoding='utf-8')

    return str(output_file)
