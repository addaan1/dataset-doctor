from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from dataset_doctor.models import ColumnProfile, DatasetProfile, HealthScore
from dataset_doctor.warnings import DatasetWarning


@dataclass(slots=True, frozen=True)
class ReportPayload:
    profile: DatasetProfile
    warnings: list[DatasetWarning]
    score: HealthScore
    suggested_actions: list[str]
    problematic_columns: list[ColumnProfile]
    numeric_columns: list[ColumnProfile]
    generated_at: str


def build_report_payload(
    profile: DatasetProfile,
    warnings: list[DatasetWarning],
    generated_at: str | None = None,
) -> ReportPayload:
    timestamp = generated_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    problematic_columns = [
        column
        for column in sorted(
            profile.columns,
            key=lambda column: (
                -column.issue_count,
                -column.missing_pct,
                -_outlier_pct(column),
                column.name,
            ),
        )
        if column.issue_count > 0
    ]
    numeric_columns = [column for column in profile.columns if column.numeric_summary is not None]

    return ReportPayload(
        profile=profile,
        warnings=warnings,
        score=calculate_health_score(profile),
        suggested_actions=_collect_suggested_actions(warnings),
        problematic_columns=problematic_columns,
        numeric_columns=numeric_columns,
        generated_at=timestamp,
    )


def calculate_health_score(profile: DatasetProfile) -> HealthScore:
    # Dimensional Scoring
    
    # 1. Completeness: penalize high missing rates
    comp_penalty = 0
    for col in profile.columns:
        if col.missing_pct >= 50.0:
            comp_penalty += 30
        elif col.flagged_missing:
            comp_penalty += 15
    completeness = max(0, 100 - comp_penalty)
    
    # 2. Uniqueness: penalize exact duplicate rows & high cardinality IDs that aren't marked as IDs
    uniq_penalty = 0
    if profile.duplicate_pct >= 10.0:
        uniq_penalty += 30
    elif profile.duplicate_rows > 0:
        uniq_penalty += 10
        
    for col in profile.columns:
        if col.is_high_cardinality and col.role != "id":
             uniq_penalty += 10
    uniqueness = max(0, 100 - uniq_penalty)
             
    # 3. Consistency: penalize mixed types, constant columns, parse failures
    cons_penalty = min(len(profile.constant_columns) * 10, 20)
    for col in profile.columns:
        if col.is_mixed_type:
             cons_penalty += 20
        if col.parse_failure_pct > 0.0:
             cons_penalty += 20
    consistency = max(0, 100 - cons_penalty)
    
    # 4. Numeric Stability: penalize extreme outliers unless heavy tail is allowed
    stab_penalty = 0
    for col in profile.outlier_columns:
        col_prof = next((c for c in profile.columns if c.name == col), None)
        if col_prof and col_prof.override.allow_heavy_tail is not True:
            stab_penalty += 10
    stability = max(0, 100 - min(stab_penalty, 40))

    # Overall Score = Weighted average
    # Give Completeness and Consistency slightly higher weight for structural safety.
    overall = int((completeness * 0.3) + (consistency * 0.3) + (uniqueness * 0.2) + (stability * 0.2))

    if overall >= 85:
        badge = "Healthy"
    elif overall >= 60:
        badge = "Needs Review"
    else:
        badge = "Critical"

    return HealthScore(
        value=overall, 
        badge=badge,
        completeness=completeness,
        uniqueness=uniqueness,
        consistency=consistency,
        stability=stability
    )


def render_markdown_summary(payload: ReportPayload) -> str:
    lines = [
        "# Dataset Doctor Summary",
        "",
        f"- Generated at: {payload.generated_at}",
        f"- Source: {payload.profile.source_name}",
        "",
        "## Overview",
        "",
        f"- Rows: {payload.profile.row_count}",
        f"- Columns: {payload.profile.column_count}",
        f"- Duplicate rows: {payload.profile.duplicate_rows} ({payload.profile.duplicate_pct:.1f}%)",
        f"- Suspicious columns: {payload.profile.suspicious_column_count}",
        "",
        "## Health Score",
        "",
        f"- Overall: {payload.score.value}/100 ({payload.score.badge})",
        f"  - Completeness: {payload.score.completeness}/100",
        f"  - Uniqueness:   {payload.score.uniqueness}/100",
        f"  - Consistency:  {payload.score.consistency}/100",
        f"  - Stability:    {payload.score.stability}/100",
        "",
        "## Top Warnings",
        "",
    ]

    for warning in payload.warnings[:5]:
        lines.append(
            f"1. **{warning.level.upper()}** - {warning.title}: {warning.message}"
        )

    if not payload.warnings:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Problematic Columns",
            "",
            "| Column | Role | Type | Missing % | Unique Ratio | Flags |",
            "| --- | --- | --- | ---: | ---: | --- |",
        ]
    )

    if payload.problematic_columns:
        for column in payload.problematic_columns:
            lines.append(
                f"| {column.name} | {column.role or '-'} | {column.semantic_type} | {column.missing_pct:.1f}% | "
                f"{column.unique_ratio:.1%} | {', '.join(column.flags)} |"
            )
    else:
        lines.append("| None | - | - | - | - | - |")

    lines.extend(
        [
            "",
            "## Numeric Findings",
            "",
            "| Column | Min | Median | Mean | Max | Std | Outliers |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )

    if payload.numeric_columns:
        for column in payload.numeric_columns:
            numeric = column.numeric_summary
            assert numeric is not None
            lines.append(
                f"| {column.name} | {_format_number(numeric.min_value)} | "
                f"{_format_number(numeric.median)} | {_format_number(numeric.mean)} | "
                f"{_format_number(numeric.max_value)} | {_format_number(numeric.std)} | "
                f"{numeric.outlier_count} ({numeric.outlier_pct:.1f}%) |"
            )
    else:
        lines.append("| None | - | - | - | - | - | - |")

    lines.extend(["", "## Suggested Actions", ""])
    for action in payload.suggested_actions:
        lines.append(f"- {action}")

    if not payload.suggested_actions:
        lines.append("- No immediate actions suggested.")

    return "\n".join(lines)


def render_html_report(payload: ReportPayload) -> str:
    template_dir = Path(__file__).with_name("templates")
    environment = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html"]),
    )
    environment.filters["number"] = _format_number
    template = environment.get_template("report.html.j2")
    return template.render(payload=payload)


def write_report_files(
    payload: ReportPayload,
    output_root: Path,
    dataset_stem: str,
) -> dict[str, Path]:
    target_dir = output_root / _sanitize_dataset_stem(dataset_stem)
    target_dir.mkdir(parents=True, exist_ok=True)

    summary_path = target_dir / "summary.md"
    html_path = target_dir / "report.html"
    summary_path.write_text(render_markdown_summary(payload), encoding="utf-8")
    html_path.write_text(render_html_report(payload), encoding="utf-8")

    return {
        "summary": summary_path.resolve(),
        "html": html_path.resolve(),
    }


def _collect_suggested_actions(warnings: list[DatasetWarning]) -> list[str]:
    actions: list[str] = []
    seen: set[str] = set()
    for warning in warnings:
        if warning.recommended_action not in seen:
            seen.add(warning.recommended_action)
            actions.append(warning.recommended_action)
    return actions


def _outlier_pct(column: ColumnProfile) -> float:
    if column.numeric_summary is None:
        return 0.0
    return column.numeric_summary.outlier_pct


def _sanitize_dataset_stem(dataset_stem: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", dataset_stem).strip("._") or "dataset"


def _format_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return f"{value:.2f}"
