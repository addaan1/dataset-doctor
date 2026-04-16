# Dataset Doctor

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/pandas-2.x-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Typer](https://img.shields.io/badge/CLI-Typer-009688)](https://typer.tiangolo.com/)
[![Jinja2](https://img.shields.io/badge/templates-Jinja2-B41717)](https://jinja.palletsprojects.com/)
[![Pytest](https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white)](https://pytest.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-111827)](LICENSE)

![Dataset Doctor Banner](data/assets/readme_banner.png)

Turn messy CSV files into an instant data health report.

Dataset Doctor is an open-source Python CLI for fast first-pass dataset checks. Point it at a CSV file and it will profile structure, missingness, duplicate rows, semantic column types, numeric distributions, outliers, uniqueness patterns, constant columns, and high-cardinality fields, then generate shareable Markdown and HTML reports.

## Why this project exists

Many CSV files look usable until hidden issues derail the workflow: sparse columns, accidental duplicates, ID-like fields masquerading as categories, suspicious numeric spikes, or columns that carry no information at all. Dataset Doctor is meant to surface those problems in seconds with a small command-line tool that still produces demo-friendly output.

The project supports both terminal inspection and generated artifacts for sharing:

- terminal summary
- `summary.md`
- `report.html`

## What the CLI checks today

- Row count and column count
- Column names
- Per-column missing count and missing percentage
- Duplicate row count and duplicate percentage
- Semantic column types: `numeric`, `boolean`, `datetime`, `categorical`
- Per-column unique count and unique ratio
- Constant columns
- High-cardinality string columns
- Numeric summaries: `min`, `max`, `mean`, `median`, `std`, `q1`, `q3`, `iqr`
- IQR-based outlier detection
- Rule-based warnings with `info`, `warning`, and `critical`
- Health score with badge: `Healthy`, `Needs Review`, `Critical`
- Automatic Markdown and HTML report generation

## Quickstart

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Install and run:

```bash
pip install -e .[dev]
dataset-doctor data/demo/quotes_to_scrape_doctor_demo.csv
```

That command prints a terminal summary and writes:

```text
outputs/
  quotes_to_scrape_doctor_demo/
    summary.md
    report.html
```

If you only want terminal output:

```bash
dataset-doctor data/demo/quotes_to_scrape_doctor_demo.csv --terminal-only
```

If you prefer module execution during development:

```bash
python -m dataset_doctor.cli data/demo/quotes_to_scrape_doctor_demo.csv --output-dir outputs
```

## Usage

```bash
dataset-doctor PATH_TO_FILE.csv --separator "," --encoding "utf-8" --output-dir outputs
```

## Example terminal output

```text
Dataset Doctor
==============

Overview
  Source: quotes_to_scrape_doctor_demo.csv
  Rows: 11
  Columns: 7
  Duplicate rows: 1

Health Snapshot
  Score: 65/100 (Needs Review)
  High-missing columns (>30%): 1
  Constant columns: 1
  High-cardinality columns: 3
  Outlier columns: 1
  Suspicious columns: 5

Warnings
  - [CRITICAL] Column `tag_count` has 1 outliers (10.0%) using the IQR rule.
  - [WARNING] Dataset contains 1 duplicate rows (9.1% of all rows).
  - [WARNING] Column `primary_tag` has 4 missing values (36.4%).
```

## HTML preview

This is the visual direction of the generated `report.html`.

![Dataset Doctor HTML report preview](data/assets/report-preview.png)

## Generated reports

- `summary.md` gives a concise text report with overview, score, top warnings, problematic columns, numeric findings, and suggested actions.
- `report.html` renders the same information in a beautiful, modern dashboard-like layout designed to be easier to scan and suitable for presentations.

The generated HTML uses a self-contained template, so the report can be opened directly in a browser without bundling extra assets.

## Demo data

The repository includes demo data under `data/`.

- `data/raw/quotes_to_scrape_page_1.csv` is based on page 1 of [Quotes to Scrape](https://quotes.toscrape.com/), a public practice site for scraping.
- `data/demo/quotes_to_scrape_doctor_demo.csv` is a derived demo dataset built from that scraped source and intentionally includes missing values, a duplicate row, a constant column, high-cardinality fields, and a numeric outlier so the report is visually informative.

More detail is documented in [data/README.md](data/README.md).

## How the current flow works

```mermaid
flowchart LR
    A[CSV file] --> B[dataset-doctor CLI]
    B --> C[Load and normalize with pandas]
    C --> D[Profile columns, numeric stats, and outliers]
    D --> E[Generate rule-based warnings and health score]
    E --> F[Readable terminal summary]
    E --> G[summary.md]
    E --> H[report.html]
```

## Project layout

```text
data/
dataset_doctor/
  templates/
outputs/
tests/
```

## Contributing

Contributions are welcome! Please check the [CONTRIBUTING.md](CONTRIBUTING.md) guide and the open issues to get started. We use standard GitHub PR workflows.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a history of changes and releases.

## License

This project is licensed under the MIT License.
