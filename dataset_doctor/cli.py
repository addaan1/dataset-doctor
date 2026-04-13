from __future__ import annotations

from pathlib import Path
from textwrap import fill

import typer

from dataset_doctor.analyzer import DatasetLoadError, EmptyDatasetError, load_data, profile_dataset
from dataset_doctor.models import DatasetProfile

app = typer.Typer(
    add_completion=False,
    help="Run a quick health check on a CSV file.",
)


@app.command()
def main(
    csv_path: Path = typer.Argument(..., help="Path to the CSV file to inspect."),
    separator: str = typer.Option(",", "--separator", "-s", help="CSV delimiter."),
    encoding: str = typer.Option("utf-8", "--encoding", "-e", help="File encoding."),
) -> None:
    try:
        dataframe = load_data(csv_path, separator=separator, encoding=encoding)
        profile = profile_dataset(dataframe, csv_path.name)
    except EmptyDatasetError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc
    except DatasetLoadError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(render_terminal_summary(profile))


def render_terminal_summary(profile: DatasetProfile) -> str:
    sorted_columns = sorted(
        profile.columns,
        key=lambda item: (-item.issue_count, -item.missing_count, item.name),
    )

    lines = [
        "Dataset Doctor",
        "==============",
        "",
        "Overview",
        f"  Source: {profile.source_name}",
        f"  Rows: {profile.row_count}",
        f"  Columns: {profile.column_count}",
        f"  Duplicate rows: {profile.duplicate_rows}",
        "",
        "Health Snapshot",
        f"  High-missing columns (>30%): {len(profile.high_missing_columns)}",
        f"  Constant columns: {len(profile.constant_columns)}",
        f"  High-cardinality columns: {len(profile.high_cardinality_columns)}",
        f"  Suspicious columns: {profile.suspicious_column_count}",
        "",
        "Type Summary",
    ]

    for semantic_type in ("categorical", "numeric", "boolean", "datetime"):
        lines.append(f"  - {semantic_type}: {profile.semantic_type_counts.get(semantic_type, 0)}")

    lines.extend(
        [
            "",
            "Columns",
            _format_column_names(profile.column_names),
            "",
            "Missingness (sorted)",
        ]
    )

    missing_columns = [column for column in profile.columns if column.missing_count > 0]
    if not missing_columns:
        lines.append("  - None")
    else:
        for column in sorted(missing_columns, key=lambda item: (-item.missing_count, item.name)):
            suffix = " HIGH" if column.flagged_missing else ""
            lines.append(
                f"  - {column.name}: {column.missing_count} missing ({column.missing_pct:.1f}%){suffix}"
            )

    lines.extend(
        [
            "",
            "Duplicates",
            (
                "  - "
                f"{profile.duplicate_rows} duplicate rows detected "
                f"({profile.duplicate_pct:.1f}% of the dataset)"
            ),
            "",
            "Suspicious Columns",
            *_render_suspicious_columns(profile),
            "",
            "Column Profile",
        ]
    )

    for column in sorted_columns:
        flag_text = f" | flags: {', '.join(column.flags)}" if column.flags else ""
        lines.append(
            "  - "
            f"{column.name}: {column.semantic_type} ({column.raw_dtype}) | "
            f"unique {column.unique_count}/{column.non_null_count} ({column.unique_ratio:.1%}) | "
            f"missing {column.missing_pct:.1f}%{flag_text}"
        )

    return "\n".join(lines)


def _format_column_names(column_names: list[str]) -> str:
    return fill(
        ", ".join(column_names),
        width=88,
        initial_indent="  ",
        subsequent_indent="  ",
    )


def _render_suspicious_columns(profile: DatasetProfile) -> list[str]:
    suspicious_lines: list[str] = []
    columns_by_name = {column.name: column for column in profile.columns}

    for column_name in profile.suspicious_columns:
        column = columns_by_name[column_name]
        reasons: list[str] = []
        if column.flagged_missing:
            reasons.append(f"{column.missing_pct:.1f}% missing")
        if column.is_constant:
            reasons.append("constant values only")
        if column.is_high_cardinality:
            reasons.append("high-cardinality strings")

        if reasons:
            suspicious_lines.append(f"  - {column.name}: {'; '.join(reasons)}")

    if not suspicious_lines:
        suspicious_lines.append("  - None")

    return suspicious_lines


if __name__ == "__main__":
    app()
