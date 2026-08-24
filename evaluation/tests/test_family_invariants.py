"""T-03, T-04, and the extra §5 check — the metric-family invariants.

Guards A (point != bbox), B (no IoU on points), C (no point<->bbox coercion),
J (families never merged).
"""
import pytest

from evaluation.errors import FamilyCoercionError
from evaluation.families import MetricFamily, metric_family_for
from evaluation.geometry import BBox, Point, iou, point_in_box
from evaluation.matching import dedup_bboxes, select_first_box
from evaluation.evaluator import evaluate_records


def test_t03_point_never_scored_with_iou():
    # Cosmos native point belongs to the Point family, never IoU.
    assert metric_family_for("Cosmos-native-point") is MetricFamily.POINT
    with pytest.raises(FamilyCoercionError):
        iou(Point(5, 5), BBox(0, 0, 10, 10))          # point on the left
    with pytest.raises(FamilyCoercionError):
        iou(BBox(0, 0, 10, 10), Point(5, 5))          # point on the right


def test_t04_point_to_bbox_coercion_rejected():
    # A point must never be fed to bbox machinery (no silent conversion).
    with pytest.raises(FamilyCoercionError):
        dedup_bboxes([Point(1, 1)])
    with pytest.raises(FamilyCoercionError):
        select_first_box([Point(1, 1)])
    # And a bbox must never be treated as a point.
    with pytest.raises(FamilyCoercionError):
        point_in_box(BBox(0, 0, 10, 10), BBox(0, 0, 10, 10))


def _qwen_run():
    raw = [{"sample_id": "a", "raw_response": {"bbox_2d": [0, 0, 10, 10]}}]
    gt = [{"sample_id": "a", "referent_present": True, "gt_boxes": [[0, 0, 10, 10]]}]
    return evaluate_records("Qwen-native-bbox", raw, gt)


def _cosmos_run():
    raw = [{"sample_id": "a", "raw_response": {"point_2d": [500, 500]},
            "image_w": 1000, "image_h": 500}]
    gt = [{"sample_id": "a", "referent_present": True, "gt_boxes": [[400, 200, 200, 200]]}]
    return evaluate_records("Cosmos-native-point", raw, gt)


def test_extra_families_never_merged():
    # §5: Qwen native bbox -> BBox family only; Cosmos native point -> Point only.
    qwen = _qwen_run()
    cosmos = _cosmos_run()

    assert qwen["metric_family"] == "bbox"
    assert "bbox_metrics" in qwen and "point_metrics" not in qwen

    assert cosmos["metric_family"] == "point"
    assert "point_metrics" in cosmos and "bbox_metrics" not in cosmos

    # No shared accuracy key that could form a single merged leaderboard.
    assert set(qwen).isdisjoint({"point_metrics"})
    assert set(cosmos).isdisjoint({"bbox_metrics"})
