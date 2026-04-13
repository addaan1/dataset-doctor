from __future__ import annotations

from pathlib import Path

from dataset_doctor.analyzer import load_data, profile_dataset
from dataset_doctor.report import build_report_payload, render_html_report, render_markdown_summary
from dataset_doctor.warnings import generate_warnings


def test_report_payload_calculates_expected_score_and_badge() -> None:
    csv_path = Path("data/demo/quotes_to_scrape_doctor_demo.csv")
    profile = profile_dataset(load_data(csv_path), csv_path.name)
    payload = build_report_payload(profile, generate_warnings(profile), generated_at="2026-04-13 22:00:00")

    assert payload.score.value == 65
    assert payload.score.badge == "Needs Review"
    assert payload.problematic_columns[0].name == "primary_tag"
    assert payload.numeric_columns[0].name == "tag_count"


def test_markdown_summary_contains_required_sections() -> None:
    csv_path = Path("data/demo/quotes_to_scrape_doctor_demo.csv")
    profile = profile_dataset(load_data(csv_path), csv_path.name)
    payload = build_report_payload(profile, generate_warnings(profile), generated_at="2026-04-13 22:00:00")

    markdown = render_markdown_summary(payload)

    assert "## Overview" in markdown
    assert "## Health Score" in markdown
    assert "## Top Warnings" in markdown
    assert "## Problematic Columns" in markdown
    assert "## Numeric Findings" in markdown
    assert "## Suggested Actions" in markdown
    assert "Inspect extreme values in `tag_count` before modeling." in markdown


def test_html_report_contains_dashboard_sections() -> None:
    csv_path = Path("data/demo/quotes_to_scrape_doctor_demo.csv")
    profile = profile_dataset(load_data(csv_path), csv_path.name)
    payload = build_report_payload(profile, generate_warnings(profile), generated_at="2026-04-13 22:00:00")

    html = render_html_report(payload)

    assert "Dataset Doctor Report" in html
    assert "Health Score" in html
    assert "Problematic Columns" in html
    assert "Numeric Findings" in html
    assert "Needs Review" in html
