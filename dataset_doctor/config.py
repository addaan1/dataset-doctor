import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True, frozen=True)
class ColumnOverride:
    role: str | None = None  # id, target, timestamp, category, measure
    force_semantic_type: str | None = None  # numeric, datetime, categorical, boolean
    allow_high_cardinality: bool | None = None
    allow_heavy_tail: bool | None = None


@dataclass(slots=True, frozen=True)
class DatasetConfig:
    global_missing_threshold: float = 30.0
    global_cardinality_threshold: float = 0.8
    column_overrides: dict[str, ColumnOverride] = field(default_factory=dict)

    @classmethod
    def from_json(cls, config_path: Path | str | None) -> "DatasetConfig":
        if not config_path:
            return cls()
        
        path = Path(config_path)
        if not path.exists():
            return cls()
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return cls()

        missing = data.get("global_missing_threshold", 30.0)
        cardinality = data.get("global_cardinality_threshold", 0.8)
        
        overrides = {}
        for col_name, opts in data.get("columns", {}).items():
            overrides[col_name] = ColumnOverride(
                role=opts.get("role"),
                force_semantic_type=opts.get("force_semantic_type"),
                allow_high_cardinality=opts.get("allow_high_cardinality"),
                allow_heavy_tail=opts.get("allow_heavy_tail"),
            )
            
        return cls(
            global_missing_threshold=float(missing),
            global_cardinality_threshold=float(cardinality),
            column_overrides=overrides,
        )

    def get_override(self, column_name: str) -> ColumnOverride:
        return self.column_overrides.get(column_name, ColumnOverride())
