from __future__ import annotations

from dataclasses import dataclass, field
from dataset_doctor.config import ColumnOverride


@dataclass(slots=True, frozen=True)
class NumericSummary:
    min_value: float
    max_value: float
    mean: float
    median: float
    std: float
    q1: float
    q3: float
    iqr: float
    lower_bound: float
    upper_bound: float
    outlier_count: int
    outlier_pct: float

    @property
    def has_outliers(self) -> bool:
        return self.outlier_count > 0


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
    
    # Advanced / Contextual checks
    parse_failure_pct: float = 0.0
    is_mixed_type: bool = False
    
    # Role & Configs
    override: ColumnOverride = field(default_factory=ColumnOverride)
    numeric_summary: NumericSummary | None = None

    @property
    def role(self) -> str | None:
        return self.override.role

    @property
    def has_outliers(self) -> bool:
        return self.numeric_summary is not None and self.numeric_summary.has_outliers

    @property
    def issue_count(self) -> int:
        return (
            int(self.flagged_missing)
            + int(self.is_constant)
            + int(self.is_high_cardinality)
            + int(self.has_outliers)
            + int(self.is_mixed_type)
            + int(self.parse_failure_pct > 0.0)
        )

    @property
    def flags(self) -> list[str]:
        flags: list[str] = []
        if self.flagged_missing:
            flags.append("missing>=30%")
        if self.is_constant:
            flags.append("constant")
        if self.is_high_cardinality:
            flags.append("high-cardinality")
        if self.has_outliers:
            flags.append("outliers")
        if self.is_mixed_type:
            flags.append("mixed-type")
        if self.parse_failure_pct > 0.0:
            flags.append(f"parse-failures: {self.parse_failure_pct:.1f}%")
        return flags


@dataclass(slots=True, frozen=True)
class HealthScore:
    value: int
    badge: str
    completeness: int
    uniqueness: int
    consistency: int
    stability: int

    @property
    def css_modifier(self) -> str:
        return self.badge.lower().replace(" ", "-")


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
    outlier_columns: list[str]
    suspicious_columns: list[str]

    @property
    def suspicious_column_count(self) -> int:
        return len(self.suspicious_columns)

    @property
    def numeric_columns(self) -> list[ColumnProfile]:
        return [column for column in self.columns if column.semantic_type == "numeric"]
