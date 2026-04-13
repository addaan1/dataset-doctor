from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from dataset_doctor.cli import app

runner = CliRunner()


def test_cli_smoke_run_with_sample_dataset() -> None:
    sample_path = Path("examples/sample_dataset.csv")

    result = runner.invoke(app, [str(sample_path)])

    assert result.exit_code == 0
    assert "Dataset Doctor" in result.stdout
    assert "Rows: 10" in result.stdout
    assert "Duplicate rows: 1" in result.stdout
    assert "Missingness (sorted)" in result.stdout
    assert "source_system: constant values only" in result.stdout


def test_cli_returns_error_for_missing_file() -> None:
    result = runner.invoke(app, ["missing.csv"])

    assert result.exit_code == 1
    assert "Dataset file was not found" in result.stderr
