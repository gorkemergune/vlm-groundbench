"""Run manifest (docs/benchmark_protocol.md).

Every run writes a manifest capturing exactly what produced its raw outputs, so
metrics are reproducible (Rule #7). TBD fields (e.g. returned_model_version for
NIM APIs) are represented as None and are NEVER fabricated.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field

PROTOCOL_VERSION = "0.1.0-draft"  # NOT frozen; do not bump here.

# Fields that must be present (non-None) for a manifest to be valid.
REQUIRED_FIELDS = (
    "run_id",
    "experiment_id",
    "model_id",
    "capability_class",
    "condition",
    "metric_family",
    "prompt_regime",
    "dataset_role",
    "seed",
    "split_manifest_hash",
    "code_git_commit",
)

# Fields explicitly allowed to be None because docs/ marks them TBD / pending.
TBD_FIELDS = (
    "returned_model_version",  # NIM version capture — verification TBD (docs blocker E)
)


@dataclass
class RunManifest:
    run_id: str
    experiment_id: str
    model_id: str
    capability_class: str
    condition: str
    metric_family: str
    prompt_regime: str
    dataset_role: str
    seed: int
    split_manifest_hash: str
    code_git_commit: str
    contamination_suspect: bool = False
    protocol_version: str = PROTOCOL_VERSION
    prompt_registry_version: str | None = None
    model_version_or_revision: str | None = None
    returned_model_version: str | None = None      # TBD — never fabricated
    decoding_params: dict = field(default_factory=dict)
    env_hash: str | None = None
    timestamp_utc: str | None = None

    def missing_required(self) -> list[str]:
        return [f for f in REQUIRED_FIELDS if getattr(self, f) is None]

    def validate(self) -> None:
        missing = self.missing_required()
        if missing:
            raise ValueError(
                f"Manifest missing required field(s): {missing}. "
                f"(TBD fields {TBD_FIELDS} may be None but must not be fabricated.)"
            )

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, **kwargs) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, indent=2, **kwargs)
