from __future__ import annotations

from dataclasses import dataclass

from dataset_doctor.models import DatasetProfile

LEVEL_ORDER = {"critical": 0, "warning": 1, "info": 2}


@dataclass(slots=True, frozen=True)
class DatasetWarning:
    level: str
    title: str
    message: str
    column_name: str | None
    recommended_action: str


def generate_warnings(profile: DatasetProfile) -> list[DatasetWarning]:
    warnings: list[DatasetWarning] = []

    for column in profile.columns:
        if column.missing_pct >= 50.0:
            warnings.append(
                DatasetWarning(
                    level="critical",
                    title=f"Severe missing values in `{column.name}`",
                    message=(
                        f"Column `{column.name}` has {column.missing_count} missing values "
                        f"({column.missing_pct:.1f}%)."
                    ),
                    column_name=column.name,
                    recommended_action=f"Audit `{column.name}` and decide whether to impute or drop it.",
                )
            )
        elif column.flagged_missing:
            warnings.append(
                DatasetWarning(
                    level="warning",
                    title=f"High missing values in `{column.name}`",
                    message=(
                        f"Column `{column.name}` has {column.missing_count} missing values "
                        f"({column.missing_pct:.1f}%)."
                    ),
                    column_name=column.name,
                    recommended_action=f"Review null-handling for `{column.name}` before analysis.",
                )
            )

        if column.is_constant:
            warnings.append(
                DatasetWarning(
                    level="warning",
                    title=f"Constant column detected: `{column.name}`",
                    message=f"Column `{column.name}` has only one non-null unique value.",
                    column_name=column.name,
                    recommended_action=f"Consider removing `{column.name}` if it adds no signal.",
                )
            )

        if column.is_high_cardinality:
            warnings.append(
                DatasetWarning(
                    level="warning",
                    title=f"High-cardinality column detected: `{column.name}`",
                    message=(
                        f"Column `{column.name}` has a unique ratio of {column.unique_ratio:.1%}, "
                        "which often indicates IDs or unstable categories."
                    ),
                    column_name=column.name,
                    recommended_action=f"Validate whether `{column.name}` should be treated as an identifier.",
                )
            )

        if column.numeric_summary and column.numeric_summary.outlier_count > 0:
            level = "critical" if column.numeric_summary.outlier_pct >= 10.0 else "warning"
            warnings.append(
                DatasetWarning(
                    level=level,
                    title=f"Outliers detected in `{column.name}`",
                    message=(
                        f"Column `{column.name}` has {column.numeric_summary.outlier_count} outliers "
                        f"({column.numeric_summary.outlier_pct:.1f}%) using the IQR rule."
                    ),
                    column_name=column.name,
                    recommended_action=f"Inspect extreme values in `{column.name}` before modeling.",
                )
            )

    if profile.duplicate_rows >= 1:
        level = "critical" if profile.duplicate_pct >= 10.0 else "warning"
        warnings.append(
            DatasetWarning(
                level=level,
                title="Duplicate rows detected",
                message=(
                    f"Dataset contains {profile.duplicate_rows} duplicate rows "
                    f"({profile.duplicate_pct:.1f}% of all rows)."
                ),
                column_name=None,
                recommended_action="Review duplicate rows and remove exact duplicates if they are accidental.",
            )
        )

    if not warnings:
        warnings.append(
            DatasetWarning(
                level="info",
                title="Dataset looks healthy",
                message="No high-severity structural issues were detected in the current dataset.",
                column_name=None,
                recommended_action="Proceed with deeper exploration or feature-specific validation.",
            )
        )
    elif profile.numeric_columns and not profile.outlier_columns:
        warnings.append(
            DatasetWarning(
                level="info",
                title="Numeric columns look stable",
                message="No numeric outliers were detected with the current IQR rule.",
                column_name=None,
                recommended_action="Keep the current numeric checks and validate domain-specific ranges next.",
            )
        )

    return sorted(
        warnings,
        key=lambda warning: (
            LEVEL_ORDER.get(warning.level, 99),
            warning.column_name or "",
            warning.title,
        ),
    )
