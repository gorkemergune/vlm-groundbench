"""Normalized per-sample result consumed by the metric functions.

GT is ALWAYS a list of BBox (invariant D); there is no point GT. A point
prediction is evaluated against the SAME bbox GT via point-in-GT-box.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .families import MetricFamily
from .geometry import BBox, Point


@dataclass
class SampleResult:
    sample_id: str
    metric_family: MetricFamily
    referent_present: bool
    gt_boxes: list[BBox]                    # ALWAYS bboxes (invariant D)
    pred_bbox: BBox | None = None           # set only for BBox-family samples
    pred_point: Point | None = None         # set only for Point-family samples
    extra_bboxes: list[BBox] = field(default_factory=list)  # additional predicted boxes
    parse_success: bool = False
    not_present: bool = False               # model declined (valid, != parse failure)
    # Post-preprocessing image size, needed for the Point-family normalized point
    # error (s_i = image diagonal). Appended at the END with defaults so existing
    # positional SampleResult(...) constructions keep working.
    image_w: float | None = None
    image_h: float | None = None

    def has_prediction(self) -> bool:
        return self.pred_bbox is not None or self.pred_point is not None
