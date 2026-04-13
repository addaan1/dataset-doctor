from __future__ import annotations

from pathlib import Path

import pandas as pd

from dataset_doctor.analyzer import load_data, profile_dataset
from dataset_doctor.warnings import generate_warnings


def test_generate_warnings_for_demo_dataset_covers_expected_issue_types() -> None:
    csv_path = Path("data/demo/quotes_to_scrape_doctor_demo.csv")
    profile = profile_dataset(load_data(csv_path), csv_path.name)

    warnings = generate_warnings(profile)

    assert any(
        warning.level == "warning" and warning.column_name == "primary_tag"
        for warning in warnings
    )
    assert any(
        warning.level == "critical" and warning.column_name == "tag_count"
        for warning in warnings
    )
    assert any(
        warning.level == "warning" and warning.column_name == "source_site"
        for warning in warnings
    )
    assert any(
        warning.level == "warning" and warning.column_name is None and "Duplicate rows" in warning.title
        for warning in warnings
    )


def test_generate_warnings_adds_info_for_healthy_dataset() -> None:
    dataframe = pd.DataFrame(
        {
            "value": [10, 11, 12, 13],
            "status": ["yes", "no", "yes", "no"],
        }
    )

    warnings = generate_warnings(profile_dataset(dataframe, "clean.csv"))

    assert len(warnings) == 1
    assert warnings[0].level == "info"
    assert "healthy" in warnings[0].title.lower()
