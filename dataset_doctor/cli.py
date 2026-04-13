from __future__ import annotations

from pathlib import Path

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
        "Columns",
        f"  {', '.join(profile.column_names)}",
        "",
        "Missingness (sorted)",
    ]

    for column in sorted(profile.columns, key=lambda item: (-item.missing_count, item.name)):
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
                f"({(profile.duplicate_rows / profile.row_count * 100):.1f}% of the dataset)"
            ),
            "",
            "Column Profile",
        ]
    )

    for column in profile.columns:
        flags: list[str] = []
        if column.flagged_missing:
            flags.append("missing>30%")
        if column.is_constant:
            flags.append("constant")
        if column.is_high_cardinality:
            flags.append("high-cardinality")
        flag_text = f" | flags: {', '.join(flags)}" if flags else ""
        lines.append(
            "  - "
            f"{column.name}: {column.semantic_type} ({column.raw_dtype}) | "
            f"unique {column.unique_count}/{column.non_null_count} ({column.unique_ratio:.1%}) | "
            f"missing {column.missing_pct:.1f}%{flag_text}"
        )

    suspicious_lines = _render_suspicious_columns(profile)
    lines.extend(["", "Suspicious Columns", *suspicious_lines])

    return "\n".join(lines)


def _render_suspicious_columns(profile: DatasetProfile) -> list[str]:
    suspicious_lines: list[str] = []

    for column in profile.columns:
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

