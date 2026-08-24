"""T-01, T-02, T-06 — parser correctness and parse-success separation.

Guards invariants E (Cosmos=point_2d), F (Qwen=bbox), G (parse failure separate).
"""
from evaluation.geometry import BBox, Point, cosmos_norm_point_to_pixel
from evaluation.metrics import acc_at_iou
from evaluation.families import MetricFamily
from evaluation.parsers import parse_cosmos_point, parse_prompted_bbox, parse_qwen_bbox
from evaluation.types import SampleResult


def test_t01_qwen_bbox_parser():
    # Qwen native bbox_2d = [x1,y1,x2,y2] absolute px -> canonical xywh.
    pr = parse_qwen_bbox({"bbox_2d": [10, 20, 110, 120]})
    assert pr.success is True
    assert pr.primitive == "bbox"
    assert pr.bbox == BBox(10, 20, 100, 100)  # w=110-10, h=120-20


def test_t02_cosmos_point_parser_and_conversion():
    # Cosmos native point_2d normalized 0-1000 -> pixel via (W/1000, H/1000).
    pr = parse_cosmos_point({"point_2d": [500, 500]})
    assert pr.success is True
    assert pr.primitive == "point"
    assert pr.norm_point == (500.0, 500.0)
    px = cosmos_norm_point_to_pixel(*pr.norm_point, image_w=1000, image_h=500)
    assert px == Point(500.0, 250.0)   # x=500*1000/1000, y=500*500/1000


def test_t06_prompted_bbox_parser_success_flags():
    # valid JSON -> success
    assert parse_prompted_bbox({"bbox_2d": [1, 2, 3, 4]}).success is True
    # valid free-text with >=4 numbers -> success
    assert parse_prompted_bbox("the box is 10 20 110 120").success is True
    # unparseable -> parse failure (success False, not a decline)
    bad = parse_prompted_bbox("I cannot find that object.")
    assert bad.success is False and bad.not_present is False
    # explicit decline -> NOT a parse failure; tracked separately (invariant G)
    dec = parse_prompted_bbox("NOT_PRESENT")
    assert dec.success is False and dec.not_present is True


def test_t06_parse_failure_not_silently_zero():
    # A parse-failed present sample is CHARGED in one basis but EXCLUDED (None)
    # in the other — never silently scored zero in the localization-only basis.
    s = SampleResult(sample_id="s1", metric_family=MetricFamily.BBOX,
                     referent_present=True, gt_boxes=[BBox(0, 0, 10, 10)],
                     pred_bbox=None, parse_success=False)
    res = acc_at_iou([s], 0.5)
    assert res["n_charged"] == 1 and res["acc_charged"] == 0.0
    assert res["n_excluded"] == 0 and res["acc_excluded"] is None
