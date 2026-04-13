"""Dataset Doctor package."""

from dataset_doctor.analyzer import (
    DatasetLoadError,
    EmptyDatasetError,
    load_data,
    profile_dataset,
    summarize_columns,
)

__all__ = [
    "DatasetLoadError",
    "EmptyDatasetError",
    "load_data",
    "profile_dataset",
    "summarize_columns",
]

__version__ = "0.1.0.dev0"

