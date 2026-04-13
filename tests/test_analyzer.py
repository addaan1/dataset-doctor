from __future__ import annotations

import pandas as pd
import pytest

from dataset_doctor.analyzer import EmptyDatasetError, load_data, profile_dataset, summarize_columns


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
    assert profile.missing_ranked_columns == ["email", "status", "id"]
    assert profile.high_missing_columns == ["email"]


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


def test_load_data_raises_for_header_only_csv(tmp_path) -> None:
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("id,name\n", encoding="utf-8")

    with pytest.raises(EmptyDatasetError):
        load_data(csv_path)


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

