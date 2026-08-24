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
from .geometry import (
    center_distance_px as geo_center_distance_px,
    image_diagonal as geo_image_diagonal,
    iou,
    point_in_box,
)
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


def normalized_point_error(samples: list[SampleResult]) -> dict:
    """SECONDARY point-family metric (docs/metrics_spec.md, Karar 2).

        s_i   = image diagonal = sqrt(W^2 + H^2)   (LOCKED)
        NPE_i = || point - center(GT box) ||_2 / s_i

    GT reference point = GT bounding box center (existing definition). A point is
    never scored with IoU and never converted to a bbox. Reports median NPE over
    present point-family samples that have a parsed point and image dimensions.
    Requires image_w/image_h on the sample; if missing, raises TBDBlocker rather
    than guessing a scale.
    """
    vals: list[float] = []
    for s in samples:
        if s.metric_family is not MetricFamily.POINT or not s.referent_present:
            continue
        if not (s.parse_success and s.pred_point is not None and s.gt_boxes):
            continue
        if s.image_w is None or s.image_h is None:
            raise TBDBlocker(
                "normalized_point_error needs image_w/image_h to form the image "
                "diagonal s_i; it is missing and must not be guessed."
            )
        s_i = geo_image_diagonal(s.image_w, s.image_h)
        if s_i <= 0.0:
            continue
        vals.append(geo_center_distance_px(s.pred_point, s.gt_boxes[0]) / s_i)
    vals.sort()
    n = len(vals)
    median = None
    if n:
        median = vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2.0
    return {"median_npe": median, "n": n, "scale": "image_diagonal"}


# ----------------------------------------------------- Cross-family utilities ---
def parse_success_rate(samples: list[SampleResult]) -> float | None:
    """Parse-success over PRESENT, NON-DECLINING samples (docs/metrics_spec.md, Karar 1).

    Population = { referent_present == True AND model did NOT return NOT_PRESENT }.
    Per-sample: valid -> num+1, den+1; parse-fail -> num+0, den+1; NOT_PRESENT
    decline -> excluded from the denominator; negative probe -> not in population.
    Reported separately, never folded into accuracy (invariant G). Preserves:
    parse failure != localization failure != negative-probe decline.
    """
    population = [s for s in samples if s.referent_present and not s.not_present]
    if not population:
        return None
    return sum(1 for s in population if s.parse_success) / len(population)


def correct_decline_rate(samples: list[SampleResult]) -> dict:
    """Negative-probe correct-decline rate (reported separately from parse-success).

    Over negative probes (referent_present == False), the fraction where the model
    correctly returned NOT_PRESENT. Complements `hall_absent` (see hallucination()).
    """
    negatives = [s for s in samples if not s.referent_present]
    n = len(negatives)
    if not n:
        return {"correct_decline": None, "n": 0}
    return {"correct_decline": sum(1 for s in negatives if s.not_present) / n, "n": n}


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
