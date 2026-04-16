from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from dataset_doctor.cli import app

runner = CliRunner()


def test_cli_default_run_writes_summary_and_html_reports(tmp_path) -> None:
    sample_path = Path("data/demo/quotes_to_scrape_doctor_demo.csv")

    result = runner.invoke(app, [str(sample_path), "--output-dir", str(tmp_path)])

    target_dir = tmp_path / "quotes_to_scrape_doctor_demo"
    summary_path = target_dir / "summary.md"
    html_path = target_dir / "report.html"

    assert result.exit_code == 0
    assert "Dataset Doctor" in result.stdout
    assert "Score: " in result.stdout
    assert "Completeness:" in result.stdout
    assert "Uniqueness:" in result.stdout
    assert "Consistency:" in result.stdout
    assert "Stability:" in result.stdout
    assert "Outlier columns: 1" not in result.stdout # Suspicious columns count is what we print now, removed the direct summary line. Actually wait, let's keep check for "tag_count"
    assert "tag_count:" in result.stdout
    assert "Written Files" in result.stdout
    assert str(summary_path.resolve()) in result.stdout
    assert str(html_path.resolve()) in result.stdout
    assert summary_path.exists() is True
    assert html_path.exists() is True


def test_cli_terminal_only_skips_file_generation(tmp_path) -> None:
    sample_path = Path("data/demo/quotes_to_scrape_doctor_demo.csv")

    result = runner.invoke(
        app,
        [str(sample_path), "--output-dir", str(tmp_path), "--terminal-only"],
    )

    target_dir = tmp_path / "quotes_to_scrape_doctor_demo"

    assert result.exit_code == 0
    assert "Written Files" not in result.stdout
    assert target_dir.exists() is False


def test_cli_returns_error_for_missing_file() -> None:
    result = runner.invoke(app, ["missing.csv"])

    assert result.exit_code == 1
    assert "Dataset file was not found" in result.stderr


def test_cli_handles_raw_scraped_csv_without_crashing(tmp_path) -> None:
    sample_path = Path("data/raw/quotes_to_scrape_page_1.csv")

    result = runner.invoke(app, [str(sample_path), "--output-dir", str(tmp_path)])

    assert result.exit_code == 0
    assert "Rows: 10" in result.stdout
    assert "Score:" in result.stdout
