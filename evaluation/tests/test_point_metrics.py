"""T-05 — point-in-GT-box (Point family primary metric).

Boundary is INCLUSIVE ("inside (or on)") per docs/metrics_spec.md.
Guards D (GT is bbox) and B (points scored against bbox GT, not IoU).
"""
from evaluation.geometry import BBox, Point, point_in_box
from evaluation.families import MetricFamily
from evaluation.metrics import point_in_gt_box_accuracy
from evaluation.types import SampleResult

GT = BBox(10, 10, 20, 20)  # xyxy = (10,10,30,30)


def test_t05_point_inside_outside_boundary():
    assert point_in_box(Point(15, 15), GT) is True    # inside  -> P-IN
    assert point_in_box(Point(5, 5), GT) is False     # outside -> P-OUT
    assert point_in_box(Point(10, 10), GT) is True    # on corner -> inclusive
    assert point_in_box(Point(30, 30), GT) is True    # far corner -> inclusive


def test_t05_point_in_gt_box_accuracy():
    inside = SampleResult(sample_id="in", metric_family=MetricFamily.POINT,
                          referent_present=True, gt_boxes=[GT],
                          pred_point=Point(15, 15), parse_success=True)
    outside = SampleResult(sample_id="out", metric_family=MetricFamily.POINT,
                           referent_present=True, gt_boxes=[GT],
                           pred_point=Point(0, 0), parse_success=True)
    res = point_in_gt_box_accuracy([inside, outside])
    assert res["n_charged"] == 2
    assert res["acc_charged"] == 0.5
    assert res["acc_excluded"] == 0.5
