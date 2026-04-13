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

    @property
    def issue_count(self) -> int:
        return int(self.flagged_missing) + int(self.is_constant) + int(self.is_high_cardinality)

    @property
    def flags(self) -> list[str]:
        flags: list[str] = []
        if self.flagged_missing:
            flags.append("missing>30%")
        if self.is_constant:
            flags.append("constant")
        if self.is_high_cardinality:
            flags.append("high-cardinality")
        return flags


@dataclass(slots=True, frozen=True)
class DatasetProfile:
    source_name: str
    row_count: int
    column_count: int
    column_names: list[str]
    duplicate_rows: int
    duplicate_pct: float
    columns: list[ColumnProfile]
    semantic_type_counts: dict[str, int]
    missing_ranked_columns: list[str]
    high_missing_columns: list[str]
    constant_columns: list[str]
    high_cardinality_columns: list[str]
    suspicious_columns: list[str]

    @property
    def suspicious_column_count(self) -> int:
        return len(self.suspicious_columns)
