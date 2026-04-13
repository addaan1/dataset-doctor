"""Dataset Doctor package."""

from dataset_doctor.analyzer import (
    DatasetLoadError,
    EmptyDatasetError,
    load_data,
    profile_dataset,
    summarize_columns,
)
from dataset_doctor.report import (
    build_report_payload,
    render_html_report,
    render_markdown_summary,
)
from dataset_doctor.warnings import generate_warnings

__all__ = [
    "DatasetLoadError",
    "EmptyDatasetError",
    "build_report_payload",
    "generate_warnings",
    "load_data",
    "profile_dataset",
    "render_html_report",
    "render_markdown_summary",
    "summarize_columns",
]

__version__ = "0.1.0.dev0"
