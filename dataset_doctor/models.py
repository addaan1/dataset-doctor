from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ColumnProfile:
    name: str
    raw_dtype: str
    semantic_type: str
    non_null_count: int
    missing_count: int
    missing_pct: float
    unique_count: int
    unique_ratio: float
    flagged_missing: bool
    is_constant: bool
    is_high_cardinality: bool


@dataclass(slots=True, frozen=True)
class DatasetProfile:
    source_name: str
    row_count: int
    column_count: int
    column_names: list[str]
    duplicate_rows: int
    columns: list[ColumnProfile]
    missing_ranked_columns: list[str]
    high_missing_columns: list[str]
    constant_columns: list[str]
    high_cardinality_columns: list[str]

