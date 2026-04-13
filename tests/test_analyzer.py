from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from dataset_doctor.analyzer import DatasetLoadError, EmptyDatasetError, load_data, profile_dataset, summarize_columns


def test_profile_dataset_ranks_missing_columns_and_counts_duplicates() -> None:
    dataframe = pd.DataFrame(
        [
            {"id": "A-1", "email": "a@example.com", "status": "active"},
            {"id": "A-2", "email": None, "status": "active"},
            {"id": "A-2", "email": None, "status": "active"},
            {"id": "A-4", "email": None, "status": None},
        ]
    )

    profile = profile_dataset(dataframe, "inline.csv")

    assert profile.duplicate_rows == 1
    assert profile.duplicate_pct == 25.0
    assert profile.missing_ranked_columns == ["email", "status", "id"]
    assert profile.high_missing_columns == ["email"]
    assert profile.suspicious_columns == ["email", "status"]


def test_summarize_columns_flags_constant_and_high_cardinality_columns() -> None:
    dataframe = pd.DataFrame(
        {
            "user_id": ["U1", "U2", "U3", "U4", "U5"],
            "source_system": ["crm", "crm", "crm", "crm", "crm"],
        }
    )

    columns = {column.name: column for column in summarize_columns(dataframe)}

    assert columns["user_id"].is_high_cardinality is True
    assert columns["source_system"].is_constant is True


def test_semantic_type_detection_matrix() -> None:
    dataframe = pd.DataFrame(
        {
            "amount": [10, 20, 30],
            "is_active": ["yes", "no", "yes"],
            "signup_date": ["2026-01-01", "2026-01-02", "2026-01-03"],
            "plan": ["basic", "pro", "basic"],
        }
    )

    columns = {column.name: column.semantic_type for column in summarize_columns(dataframe)}

    assert columns == {
        "amount": "numeric",
        "is_active": "boolean",
        "signup_date": "datetime",
        "plan": "categorical",
    }


def test_numeric_summary_uses_iqr_for_outlier_detection() -> None:
    dataframe = pd.DataFrame({"value": [10, 12, 13, 14, 100]})

    column = summarize_columns(dataframe)[0]
    assert column.numeric_summary is not None
    assert column.numeric_summary.outlier_count == 1
    assert column.numeric_summary.outlier_pct == 20.0
    assert column.numeric_summary.upper_bound < 100


def test_numeric_summary_skips_outlier_detection_for_small_numeric_samples() -> None:
    dataframe = pd.DataFrame({"value": [1, 2, 99]})

    column = summarize_columns(dataframe)[0]
    assert column.numeric_summary is not None
    assert column.numeric_summary.outlier_count == 0
    assert column.numeric_summary.outlier_pct == 0.0


def test_load_data_raises_for_header_only_csv(tmp_path) -> None:
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("id,name\n", encoding="utf-8")

    with pytest.raises(EmptyDatasetError):
        load_data(csv_path)


def test_load_data_rejects_directory(tmp_path) -> None:
    with pytest.raises(DatasetLoadError, match="Expected a CSV file but received a directory"):
        load_data(tmp_path)


def test_all_null_columns_are_not_marked_constant() -> None:
    dataframe = pd.DataFrame(
        {
            "notes": pd.Series([None, None, None], dtype="object"),
            "score": [1, 2, 3],
        }
    )

    columns = {column.name: column for column in summarize_columns(dataframe)}

    assert columns["notes"].missing_pct == 100.0
    assert columns["notes"].unique_count == 0
    assert columns["notes"].is_constant is False
    assert columns["notes"].is_high_cardinality is False


def test_load_data_normalizes_whitespace_only_strings(tmp_path) -> None:
    csv_path = tmp_path / "whitespace.csv"
    csv_path.write_text("name,comment\nAlice,   \nBob,Looks good\n", encoding="utf-8")

    dataframe = load_data(csv_path)
    columns = {column.name: column for column in summarize_columns(dataframe)}

    assert columns["comment"].missing_count == 1
    assert columns["comment"].missing_pct == 50.0


def test_profile_dataset_tracks_semantic_type_counts_and_outlier_columns() -> None:
    csv_path = Path("data/demo/quotes_to_scrape_doctor_demo.csv")
    dataframe = load_data(csv_path)

    profile = profile_dataset(dataframe, csv_path.name)

    assert profile.semantic_type_counts == {
        "categorical": 5,
        "numeric": 1,
        "boolean": 0,
        "datetime": 1,
    }
    assert profile.outlier_columns == ["tag_count"]
    assert profile.suspicious_columns[:5] == [
        "primary_tag",
        "tag_count",
        "quote_id",
        "quote_text",
        "source_site",
    ]
