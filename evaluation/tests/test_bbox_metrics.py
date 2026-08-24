"""T-07, T-08 — BBox family IoU / Acc@IoU and duplicate handling.

Guards the primary BBox metric (Acc@IoU) and the locked dedup rule (IoU >= 0.95).
"""
from evaluation.geometry import BBox, iou
from evaluation.families import MetricFamily
from evaluation.matching import dedup_bboxes, select_first_box
from evaluation.metrics import acc_at_iou
from evaluation.types import SampleResult


def test_t07_iou_known_pairs():
    assert iou(BBox(0, 0, 10, 10), BBox(0, 0, 10, 10)) == 1.0
    # inter=90, union=110 -> 0.8181...
    assert abs(iou(BBox(0, 0, 10, 10), BBox(1, 0, 10, 10)) - (90.0 / 110.0)) < 1e-12
    # disjoint
    assert iou(BBox(0, 0, 10, 10), BBox(100, 100, 10, 10)) == 0.0


def test_t07_acc_at_iou_thresholds():
    # s1: IoU=90/110=0.818 (hit @0.5 and @0.75)
    s1 = SampleResult("s1", MetricFamily.BBOX, True, [BBox(1, 0, 10, 10)],
                      pred_bbox=BBox(0, 0, 10, 10), parse_success=True)
    # s2: IoU=80/120=0.667 (hit @0.5 only)
    s2 = SampleResult("s2", MetricFamily.BBOX, True, [BBox(2, 0, 10, 10)],
                      pred_bbox=BBox(0, 0, 10, 10), parse_success=True)
    at50 = acc_at_iou([s1, s2], 0.5)
    at75 = acc_at_iou([s1, s2], 0.75)
    assert at50["acc_charged"] == 1.0 and at50["acc_excluded"] == 1.0
    assert at75["acc_charged"] == 0.5 and at75["acc_excluded"] == 0.5
    assert at50["n_charged"] == 2 and at50["n_excluded"] == 2


def test_t08_duplicate_dedup_iou_095():
    b1 = BBox(0, 0, 100, 100)
    b1_dup = BBox(0, 0, 100, 100)          # IoU 1.0 with b1 -> duplicate
    b_near = BBox(0, 0, 100, 99)           # IoU 0.99 with b1 -> duplicate
    b_other = BBox(200, 200, 10, 10)       # distinct -> kept
    kept = dedup_bboxes([b1, b1_dup, b_near, b_other])
    assert len(kept) == 2
    assert kept[0] == b1 and kept[1] == b_other       # first-seen order preserved
    assert select_first_box([b1, b1_dup]) == b1
