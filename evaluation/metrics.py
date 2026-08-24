"""Metric functions — two SEPARATE families (invariant J).

BBox family : Acc@IoU (primary), mean IoU, parse-success, hallucination.
Point family: point-in-GT-box accuracy (primary), parse-success, hallucination.

Every accuracy is reported on TWO bases (docs/metrics_spec.md):
  - "charged"  : a parse failure counts as incorrect (charged to the model).
  - "excluded" : parse failures are excluded (localization-only).

A point is never scored with IoU (invariant B). GT is always a bbox (invariant D).
"""
from __future__ import annotations

from .errors import TBDBlocker
from .families import MetricFamily
from .geometry import iou, point_in_box
from .types import SampleResult


# ---------------------------------------------------------------- BBox family ---
def acc_at_iou(samples: list[SampleResult], tau: float) -> dict:
    """Acc@IoU for single-target BBox-family present samples (primary metric)."""
    present = [s for s in samples
              if s.metric_family is MetricFamily.BBOX and s.referent_present]
    n_charged = len(present)
    n_excluded = 0
    hits = 0
    hits_excluded = 0
    for s in present:
        scored = s.parse_success and s.pred_bbox is not None and s.gt_boxes
        if s.parse_success:
            n_excluded += 1
        if scored and iou(s.pred_bbox, s.gt_boxes[0]) >= tau:
            hits += 1
            hits_excluded += 1
    return {
        "tau": tau,
        "acc_charged": (hits / n_charged) if n_charged else None,
        "acc_excluded": (hits_excluded / n_excluded) if n_excluded else None,
        "n_charged": n_charged,
        "n_excluded": n_excluded,
    }


def mean_iou(samples: list[SampleResult]) -> float | None:
    vals = [iou(s.pred_bbox, s.gt_boxes[0])
            for s in samples
            if s.metric_family is MetricFamily.BBOX and s.referent_present
            and s.parse_success and s.pred_bbox is not None and s.gt_boxes]
    if not vals:
        return None
    return sum(vals) / len(vals)


# --------------------------------------------------------------- Point family ---
def point_in_gt_box_accuracy(samples: list[SampleResult]) -> dict:
    """Primary point-family metric: fraction of points inside the GT bbox.

    Scored against the SAME bbox GT (invariant D); never uses IoU (invariant B).
    """
    present = [s for s in samples
              if s.metric_family is MetricFamily.POINT and s.referent_present]
    n_charged = len(present)
    n_excluded = 0
    hits = 0
    for s in present:
        if s.parse_success:
            n_excluded += 1
        if s.parse_success and s.pred_point is not None \
                and any(point_in_box(s.pred_point, gt) for gt in s.gt_boxes):
            hits += 1
    return {
        "acc_charged": (hits / n_charged) if n_charged else None,
        "acc_excluded": (hits / n_excluded) if n_excluded else None,
        "n_charged": n_charged,
        "n_excluded": n_excluded,
    }


def normalized_point_error(*_args, **_kwargs):
    """Normalized point error — BLOCKED: scale s_i is TBD in docs/.

    docs/metrics_spec.md leaves s_i (image-diagonal vs sqrt(area)) as TBD. We do
    not pick one. Raw pixel center-distance is available via
    geometry.center_distance_px (no decision required).
    """
    raise TBDBlocker(
        "normalized_point_error requires the scale s_i, which is TBD in "
        "docs/metrics_spec.md (image-diagonal vs sqrt(area)). Resolve in docs first."
    )


# ----------------------------------------------------- Cross-family utilities ---
def parse_success_rate(samples: list[SampleResult]) -> float | None:
    """Parse-success over PRESENT samples (a box/point is expected there).

    Reported separately, never folded into accuracy (invariant G). NOTE: whether
    negative probes belong in the denominator is a minor ambiguity in
    docs/metrics_spec.md; we scope this to present samples and flag the ambiguity
    to the human rather than deciding it silently.
    """
    present = [s for s in samples if s.referent_present]
    if not present:
        return None
    return sum(1 for s in present if s.parse_success) / len(present)


def hallucination(samples: list[SampleResult]) -> dict:
    """hall_absent (both families), hall_wrongbox (bbox), hall_wrongpoint (point).

    A correct NOT_PRESENT on an absent referent is NOT a hallucination and NOT a
    miss (docs/metrics_spec.md).
    """
    negatives = [s for s in samples if not s.referent_present]
    n_neg = len(negatives)
    absent_hits = sum(1 for s in negatives if (not s.not_present) and s.has_prediction())

    bbox_present = [s for s in samples
                    if s.metric_family is MetricFamily.BBOX and s.referent_present
                    and s.parse_success and s.pred_bbox is not None]
    wrongbox = sum(1 for s in bbox_present
                   if all(iou(s.pred_bbox, gt) == 0.0 for gt in s.gt_boxes))

    point_present = [s for s in samples
                     if s.metric_family is MetricFamily.POINT and s.referent_present
                     and s.parse_success and s.pred_point is not None]
    wrongpoint = sum(1 for s in point_present
                     if not any(point_in_box(s.pred_point, gt) for gt in s.gt_boxes))

    return {
        "hall_absent": (absent_hits / n_neg) if n_neg else None,
        "hall_absent_n": n_neg,
        "hall_wrongbox": (wrongbox / len(bbox_present)) if bbox_present else None,
        "hall_wrongbox_n": len(bbox_present),
        "hall_wrongpoint": (wrongpoint / len(point_present)) if point_present else None,
        "hall_wrongpoint_n": len(point_present),
    }
