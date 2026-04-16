# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Issue templates for Bug Reports and Feature Requests.
- `CONTRIBUTING.md` guidelines for open-source contributors.
- Beautiful custom graphics (banner and HTML report layouts) for the README.

## [v0.4.0] - 2026-04-16

### Added
- **Contextual Configuration Engine:** Load JSON config (`--config`) to set column roles (`id`, `target`, etc.) and configuration overrides (e.g. `allow_heavy_tail`, `force_semantic_type`).
- **Multi-Dimensional Health Score:** The single penalty threshold has been completely revamped into 4 descriptive dimensions: `Completeness`, `Uniqueness`, `Consistency`, and `Stability`.
- **Advanced Consistency Checks:** Analyzer now detects parse failures (when enforcing semantic types) and mixed Python types inside string columns.
- **GitHub Actions CI:** Added workflow to automatically run `ruff` and `pytest` on every push/PR.

### Changed
- Dashboard HTML and Terminal Summary updated to render the new 4-dimensional health score progress bars.
- Rewrote the warnings engine to dynamically suppress false positives based on contextual column roles (e.g., suppressing high-cardinality warnings on `id` columns).
- Test suite refactored to focus on behavior-based assertions rather than exact string matching, making it robust against UI text changes.

### Changed
- Removed Day 11-14 Roadmap section from `README.md` as final phase goals (testing, polishing, documentation) are achieved.
- Revamped the UI of the generated `report.html` to resemble a modern data dashboard dashboard using an elegant teal aesthetic.

## [v0.1.0] - 2026-04-16

### Added
- Initial open-source release of Dataset Doctor.
- CLI application to parse and structure CSV datasets (`dataset-doctor`).
- Data analysis engine capable of analyzing missing values, high-cardinality, duplicates, semantic types, and calculating statistics.
- IQR-based outlier detection for numeric columns.
- Evaluation engine that flags dataset-level properties and calculates a Health Score (`Healthy`, `Needs Review`, `Critical`).
- Automatic report generation to terminal format, Markdown (`summary.md`), and HTML (`report.html`).
- Included `quotes_to_scrape_doctor_demo.csv` as an interactive demo dataset.
- 94% test coverage via `pytest`.
