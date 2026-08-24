"""Capability classes, metric families, and the condition registry.

This encodes the LOCKED mapping from docs/model_matrix.md and
docs/experiment_plan.md. It does not invent conditions or reclassify models.

Invariant J: a condition belongs to exactly ONE metric family; the two families
are never merged. Invariant E/F: native primitives are fixed per model.
"""
from __future__ import annotations

from enum import Enum


class MetricFamily(str, Enum):
    BBOX = "bbox"
    POINT = "point"


class CapabilityClass(str, Enum):
    A_BBOX = "A-bbox"   # native bounding box (Qwen)
    A_POINT = "A-point"  # native point (Cosmos)
    C = "C"             # prompt-induced coordinates (Llama x2, Nemotron)


class Regime(str, Enum):
    NATIVE = "native"
    PROMPTED = "prompted"


# condition -> (model capability class, metric family, regime, is_native)
# NOTE: capability_class is a property of the MODEL; a model can appear in a
# prompted condition (e.g. Cosmos-prompted-bbox) while remaining A-point overall.
CONDITIONS: dict[str, dict] = {
    # --- E1a: native conditions ---
    "Qwen-native-bbox": {
        "capability_class": CapabilityClass.A_BBOX,
        "metric_family": MetricFamily.BBOX,
        "regime": Regime.NATIVE,
        "is_native": True,
    },
    "Cosmos-native-point": {
        "capability_class": CapabilityClass.A_POINT,
        "metric_family": MetricFamily.POINT,
        "regime": Regime.NATIVE,
        "is_native": True,
    },
    # --- E1b: prompted bbox conditions (all five). Coordinates are prompt-induced. ---
    "Qwen-prompted-bbox": {
        "capability_class": CapabilityClass.A_BBOX,
        "metric_family": MetricFamily.BBOX,
        "regime": Regime.PROMPTED,
        "is_native": False,
    },
    "Cosmos-prompted-bbox": {
        "capability_class": CapabilityClass.A_POINT,  # model stays A-point
        "metric_family": MetricFamily.BBOX,
        "regime": Regime.PROMPTED,
        "is_native": False,  # never native bbox
    },
    "Llama-11B-prompted-bbox": {
        "capability_class": CapabilityClass.C,
        "metric_family": MetricFamily.BBOX,
        "regime": Regime.PROMPTED,
        "is_native": False,
    },
    "Llama-90B-prompted-bbox": {
        "capability_class": CapabilityClass.C,
        "metric_family": MetricFamily.BBOX,
        "regime": Regime.PROMPTED,
        "is_native": False,
    },
    "Nemotron-prompted-bbox": {
        "capability_class": CapabilityClass.C,
        "metric_family": MetricFamily.BBOX,
        "regime": Regime.PROMPTED,
        "is_native": False,
    },
}


def condition_info(condition: str) -> dict:
    if condition not in CONDITIONS:
        raise KeyError(
            f"Unknown condition {condition!r}. Known conditions are locked in "
            f"docs/experiment_plan.md: {sorted(CONDITIONS)}"
        )
    return CONDITIONS[condition]


def metric_family_for(condition: str) -> MetricFamily:
    return condition_info(condition)["metric_family"]
