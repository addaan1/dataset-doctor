from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
    is_string_dtype,
)

from dataset_doctor.models import ColumnProfile, DatasetProfile

BOOLEAN_TRUE_VALUES = {"true", "t", "yes", "y", "1"}
BOOLEAN_FALSE_VALUES = {"false", "f", "no", "n", "0"}
SEMANTIC_TYPE_ORDER = ("categorical", "numeric", "boolean", "datetime")
HIGH_MISSING_THRESHOLD_PCT = 30.0
HIGH_CARDINALITY_THRESHOLD = 0.8
DATE_HINT_PATTERN = re.compile(
    r"[-/:T]|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec",
    re.IGNORECASE,
)


class DatasetLoadError(Exception):
    """Raised when a dataset cannot be loaded."""


class EmptyDatasetError(DatasetLoadError):
    """Raised when a CSV is readable but contains no data rows."""


def load_data(path: str | Path, separator: str = ",", encoding: str = "utf-8") -> pd.DataFrame:
    csv_path = Path(path)
    if not csv_path.exists():
        raise DatasetLoadError(f"Dataset file was not found: {csv_path}")
    if not csv_path.is_file():
        raise DatasetLoadError(f"Expected a CSV file but received a directory: {csv_path}")

    try:
        dataframe = pd.read_csv(csv_path, sep=separator, encoding=encoding)
    except pd.errors.EmptyDataError as exc:
        raise EmptyDatasetError(
            "Dataset is empty. Provide a CSV with headers and at least one data row."
        ) from exc
    except UnicodeDecodeError as exc:
        raise DatasetLoadError(
            f"Could not decode CSV with encoding '{encoding}'. Try a different --encoding value."
        ) from exc
    except Exception as exc:
        raise DatasetLoadError(f"Could not read CSV file: {exc}") from exc

    dataframe = _normalize_dataframe(dataframe)

    if dataframe.empty or dataframe.columns.empty:
        raise EmptyDatasetError(
            "Dataset is empty. Provide a CSV with headers and at least one data row."
        )

    return dataframe


def summarize_columns(df: pd.DataFrame) -> list[ColumnProfile]:
    row_count = int(len(df))
    column_profiles: list[ColumnProfile] = []

    for column_name in df.columns:
        series = df[column_name]
        non_null = series.dropna()
        non_null_count = int(non_null.shape[0])
        missing_count = row_count - non_null_count
        missing_pct = (missing_count / row_count * 100) if row_count else 0.0
        unique_count = int(non_null.nunique(dropna=True))
        unique_ratio = (unique_count / non_null_count) if non_null_count else 0.0
        semantic_type = _infer_semantic_type(series)
        is_constant = non_null_count > 0 and unique_count == 1
        is_high_cardinality = (
            non_null_count > 0
            and _is_string_like(series)
            and semantic_type == "categorical"
            and unique_ratio > HIGH_CARDINALITY_THRESHOLD
        )

        column_profiles.append(
            ColumnProfile(
                name=str(column_name),
                raw_dtype=str(series.dtype),
                semantic_type=semantic_type,
                non_null_count=non_null_count,
                missing_count=missing_count,
                missing_pct=missing_pct,
                unique_count=unique_count,
                unique_ratio=unique_ratio,
                flagged_missing=missing_pct > HIGH_MISSING_THRESHOLD_PCT,
                is_constant=is_constant,
                is_high_cardinality=is_high_cardinality,
            )
        )

    return column_profiles


def profile_dataset(df: pd.DataFrame, source_name: str) -> DatasetProfile:
    columns = summarize_columns(df)
    missing_ranked = sorted(columns, key=lambda column: (-column.missing_count, column.name))
    semantic_type_counts = {semantic_type: 0 for semantic_type in SEMANTIC_TYPE_ORDER}
    for column in columns:
        semantic_type_counts[column.semantic_type] = (
            semantic_type_counts.get(column.semantic_type, 0) + 1
        )

    suspicious_columns = [
        column.name
        for column in sorted(
            columns,
            key=lambda column: (-column.issue_count, -column.missing_pct, column.name),
        )
        if column.issue_count > 0
    ]
    duplicate_rows = int(df.duplicated().sum())
    row_count = int(len(df))

    return DatasetProfile(
        source_name=source_name,
        row_count=row_count,
        column_count=int(len(df.columns)),
        column_names=[str(column_name) for column_name in df.columns],
        duplicate_rows=duplicate_rows,
        duplicate_pct=(duplicate_rows / row_count * 100) if row_count else 0.0,
        columns=columns,
        semantic_type_counts=semantic_type_counts,
        missing_ranked_columns=[column.name for column in missing_ranked],
        high_missing_columns=[column.name for column in columns if column.flagged_missing],
        constant_columns=[column.name for column in columns if column.is_constant],
        high_cardinality_columns=[column.name for column in columns if column.is_high_cardinality],
        suspicious_columns=suspicious_columns,
    )


def _infer_semantic_type(series: pd.Series) -> str:
    if is_bool_dtype(series):
        return "boolean"

    if is_numeric_dtype(series):
        return "numeric"

    if is_datetime64_any_dtype(series):
        return "datetime"

    if not _is_string_like(series):
        return "categorical"

    non_null = series.dropna()
    if non_null.empty:
        return "categorical"

    normalized = non_null.astype(str).str.strip()
    normalized_lower = {value.lower() for value in normalized if value}

    if normalized_lower and normalized_lower <= (BOOLEAN_TRUE_VALUES | BOOLEAN_FALSE_VALUES):
        return "boolean"

    sample = normalized.head(20)
    if sample.map(lambda value: bool(DATE_HINT_PATTERN.search(value))).mean() >= 0.5:
        parsed = _parse_datetimes(normalized)
        if parsed.notna().mean() >= 0.8:
            return "datetime"

    return "categorical"


def _is_string_like(series: pd.Series) -> bool:
    return is_object_dtype(series.dtype) or is_string_dtype(series.dtype)


def _parse_datetimes(values: pd.Series) -> pd.Series:
    try:
        return pd.to_datetime(values, errors="coerce", format="mixed")
    except TypeError:
        return pd.to_datetime(values, errors="coerce")


def _normalize_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    normalized = dataframe.copy()
    normalized.columns = [str(column_name).strip() for column_name in normalized.columns]

    string_columns = normalized.select_dtypes(include=["object", "string"]).columns
    if len(string_columns) > 0:
        normalized.loc[:, string_columns] = normalized.loc[:, string_columns].replace(
            r"^\s*$",
            pd.NA,
            regex=True,
        )

    return normalized
