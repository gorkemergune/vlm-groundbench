"""RunConfig — the committed definition of a single run (Rule #3).

Field set mirrors docs/experiment_plan.md (config-driven runs) and the run
manifest in docs/benchmark_protocol.md. Validation cross-checks the config
against the LOCKED condition registry so an inconsistent config fails loudly
instead of silently mis-scoring.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from evaluation.families import CapabilityClass, MetricFamily, Regime, condition_info

VALID_EXPERIMENTS = ("E1a", "E1b", "E2", "E3", "E4")  # locked; no new top-level IDs


@dataclass
class RunConfig:
    experiment_id: str
    model_id: str
    condition: str
    seed: int
    split_manifest: str
    dataset_role: str = "heldout"          # heldout | public_secondary
    contamination_suspect: bool = False
    prompt_registry_version: str | None = None
    decoding: dict = field(default_factory=lambda: {"temperature": 0})
    # output_format_spec is None until the prompt registry is frozen (TBD for
    # prompted conditions). Never fabricate a convention here.
    output_format_spec: str | None = None

    # --- derived (from the locked condition registry) ---
    @property
    def _info(self) -> dict:
        return condition_info(self.condition)

    @property
    def capability_class(self) -> CapabilityClass:
        return self._info["capability_class"]

    @property
    def metric_family(self) -> MetricFamily:
        return self._info["metric_family"]

    @property
    def prompt_regime(self) -> Regime:
        return self._info["regime"]

    def validate(self) -> None:
        if self.experiment_id not in VALID_EXPERIMENTS:
            raise ValueError(
                f"experiment_id {self.experiment_id!r} not in locked set "
                f"{VALID_EXPERIMENTS} (docs/experiment_plan.md)."
            )
        # Touch the registry to ensure the condition is known/consistent.
        _ = self._info
        if self.dataset_role not in ("heldout", "public_secondary"):
            raise ValueError(f"Unknown dataset_role {self.dataset_role!r}.")
        # Contamination flag must be consistent with role.
        if self.dataset_role == "heldout" and self.contamination_suspect:
            raise ValueError("held-out set is contamination-free; "
                             "contamination_suspect must be False for it.")
