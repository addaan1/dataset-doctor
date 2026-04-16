from __future__ import annotations

from pathlib import Path
from textwrap import fill

import typer

from dataset_doctor.analyzer import DatasetLoadError, EmptyDatasetError, load_data, profile_dataset
from dataset_doctor.config import DatasetConfig
from dataset_doctor.report import build_report_payload, write_report_files
from dataset_doctor.warnings import generate_warnings

app = typer.Typer(
    add_completion=False,
    help="Run a quick contextual health check on a CSV file.",
)


@app.command()
def main(
    csv_path: Path = typer.Argument(..., help="Path to the CSV file to inspect."),
    separator: str = typer.Option(",", "--separator", "-s", help="CSV delimiter."),
    encoding: str = typer.Option("utf-8", "--encoding", "-e", help="File encoding."),
    config: Path | None = typer.Option(None, "--config", "-c", help="Path to a JSON configuration file."),
    output_dir: Path = typer.Option(Path("outputs"), "--output-dir", help="Directory for generated report files."),
    terminal_only: bool = typer.Option(False, "--terminal-only", help="Print terminal output only and skip file generation."),
) -> None:
    # Load Configuration
    ds_config = DatasetConfig.from_json(config) if config else DatasetConfig()

    try:
        dataframe = load_data(csv_path, separator=separator, encoding=encoding)
        profile = profile_dataset(dataframe, csv_path.name, config=ds_config)
        warnings = generate_warnings(profile)
        payload = build_report_payload(profile, warnings)
    except EmptyDatasetError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc
    except DatasetLoadError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    lines = [render_terminal_summary(payload)]
    if not terminal_only:
        try:
            written_files = write_report_files(payload, output_dir, csv_path.stem)
        except OSError as exc:
            typer.secho(f"Could not write report files: {exc}", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1) from exc
        lines.append(render_written_files(written_files))

    typer.echo("\n".join(lines))


def render_terminal_summary(payload) -> str:
    profile = payload.profile
    score = payload.score
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
        f"  Score: {score.value}/100 ({score.badge})",
        f"    - Completeness: {score.completeness}/100",
        f"    - Uniqueness:   {score.uniqueness}/100",
        f"    - Consistency:  {score.consistency}/100",
        f"    - Stability:    {score.stability}/100",
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
            "Warnings",
        ]
    )

    for warning in payload.warnings[:6]:
        lines.append(f"  - [{warning.level.upper()}] {warning.message}")

    lines.extend(["", "Numeric Findings"])
    if payload.numeric_columns:
        for column in payload.numeric_columns:
            numeric = column.numeric_summary
            assert numeric is not None
            lines.append(
                "  - "
                f"{column.name}: min {_format_number(numeric.min_value)} | "
                f"median {_format_number(numeric.median)} | "
                f"mean {_format_number(numeric.mean)} | "
                f"max {_format_number(numeric.max_value)} | "
                f"outliers {numeric.outlier_count} ({numeric.outlier_pct:.1f}%)"
            )
    else:
        lines.append("  - None")

    lines.extend(["", "Suspicious Columns"])
    for column in payload.problematic_columns:
        reasons: list[str] = []
        if column.flagged_missing:
            reasons.append(f"{column.missing_pct:.1f}% missing")
        if column.is_constant:
            reasons.append("constant values only")
        if column.is_high_cardinality:
            reasons.append("high-cardinality strings")
        if column.has_outliers and column.numeric_summary is not None:
            reasons.append(
                f"{column.numeric_summary.outlier_count} outliers ({column.numeric_summary.outlier_pct:.1f}%)"
            )
        if column.is_mixed_type:
            reasons.append("mixed-type parsed")
        if column.parse_failure_pct > 0:
            reasons.append(f"{column.parse_failure_pct:.1f}% parse failure")
            
        lines.append(f"  - {column.name} (Role: {column.role or '-'}): {'; '.join(reasons)}")

    if not payload.problematic_columns:
        lines.append("  - None")

    lines.extend(["", "Column Profile (Contextual)"])
    for column in sorted(
        profile.columns,
        key=lambda item: (-item.issue_count, -item.missing_count, item.name),
    ):
        flag_text = f" | flags: {', '.join(column.flags)}" if column.flags else ""
        lines.append(
            "  - "
            f"{column.name} [{column.role or 'feature'}]: {column.semantic_type} ({column.raw_dtype}) | "
            f"unique {column.unique_count}/{column.non_null_count} ({column.unique_ratio:.1%}) | "
            f"missing {column.missing_pct:.1f}%{flag_text}"
        )

    return "\n".join(lines)


def render_written_files(written_files: dict[str, Path]) -> str:
    return "\n".join(
        [
            "",
            "Written Files",
            f"  Summary: {written_files['summary']}",
            f"  HTML Report: {written_files['html']}",
        ]
    )


def _format_column_names(column_names: list[str]) -> str:
    return fill(
        ", ".join(column_names),
        width=88,
        initial_indent="  ",
        subsequent_indent="  ",
    )


def _format_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return f"{value:.2f}"

if __name__ == "__main__":
    app()
