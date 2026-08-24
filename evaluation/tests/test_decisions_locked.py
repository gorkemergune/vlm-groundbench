"""T-13, T-14, T-15 — locked decisions (Karar 1 & Karar 2).

New tests only; existing test files are untouched.
"""
import json
import os

import pytest

from evaluation.errors import FamilyCoercionError
from evaluation.evaluator import evaluate_run
from evaluation.families import MetricFamily
from evaluation.geometry import BBox, Point, image_diagonal, iou
from evaluation.metrics import normalized_point_error, parse_success_rate
from evaluation.types import SampleResult
from experiments.config import RunConfig
from experiments.runner import write_gt, write_raw_run
from models.dummy import DummyAdapter


# --- T-13: parse_success_rate denominator (Karar 1) ---------------------------
def test_t13_parse_success_denominator():
    valid = SampleResult("v", MetricFamily.BBOX, referent_present=True,
                         gt_boxes=[BBox(0, 0, 10, 10)], pred_bbox=BBox(0, 0, 10, 10),
                         parse_success=True, not_present=False)
    parse_fail = SampleResult("f", MetricFamily.BBOX, referent_present=True,
                              gt_boxes=[BBox(0, 0, 10, 10)], pred_bbox=None,
                              parse_success=False, not_present=False)
    decline = SampleResult("d", MetricFamily.BBOX, referent_present=True,
                           gt_boxes=[BBox(0, 0, 10, 10)], pred_bbox=None,
                           parse_success=False, not_present=True)  # NOT_PRESENT
    # valid + parse-fail counted; decline excluded from denominator -> 1/2
    assert parse_success_rate([valid, parse_fail, decline]) == 0.5


def test_t13_negative_probe_not_in_population():
    valid = SampleResult("v", MetricFamily.BBOX, referent_present=True,
                         gt_boxes=[BBox(0, 0, 10, 10)], pred_bbox=BBox(0, 0, 10, 10),
                         parse_success=True)
    negative = SampleResult("n", MetricFamily.BBOX, referent_present=False,
                            gt_boxes=[], pred_bbox=None, parse_success=False,
                            not_present=True)
    # negative probe excluded from the parse-success population -> 1/1
    assert parse_success_rate([valid, negative]) == 1.0


# --- T-14: normalized point error (Karar 2) -----------------------------------
def test_t14_normalized_point_error_image_diagonal():
    # GT box center = (200, 300); point offset by (30, 40) -> distance 50.
    gt = BBox(100, 200, 200, 200)          # xyxy (100,200,300,400), center (200,300)
    s = SampleResult("p", MetricFamily.POINT, referent_present=True, gt_boxes=[gt],
                     pred_point=Point(230, 340), parse_success=True,
                     image_w=1000, image_h=500)
    diag = image_diagonal(1000, 500)       # sqrt(1_250_000) ~ 1118.0339887
    res = normalized_point_error([s])
    assert res["scale"] == "image_diagonal" and res["n"] == 1
    assert abs(res["median_npe"] - (50.0 / diag)) < 1e-9
    assert abs(res["median_npe"] - 0.04472135955) < 1e-6


def test_t14_point_never_iou_or_bbox():
    # A point is never scored with IoU and never coerced to a bbox.
    with pytest.raises(FamilyCoercionError):
        iou(Point(230, 340), BBox(100, 200, 200, 200))


# --- T-15: E2E NPE == 0 when predicted point == GT center ---------------------
def test_t15_e2e_cosmos_npe_zero(tmp_path):
    cfg = RunConfig(experiment_id="E1a", model_id="cosmos3-nano-reasoner",
                    condition="Cosmos-native-point", seed=0,
                    split_manifest="synthetic://t15")
    # point_2d=[200,400] @ W=1000,H=500 -> pixel (200,200) == center of GT box.
    adapter = DummyAdapter(cfg.model_id, {"cb1": {"point_2d": [200, 400]}})
    samples = [{"sample_id": "cb1", "image_w": 1000, "image_h": 500}]
    gt = [{"sample_id": "cb1", "referent_present": True, "gt_boxes": [[100, 100, 200, 200]]}]

    raw_dir = write_raw_run(cfg, adapter, samples, out_root=str(tmp_path))
    gt_path = write_gt(gt, os.path.join(str(tmp_path), "gt", "t15.jsonl"))
    metrics_dir = os.path.join(str(tmp_path), "metrics", "t15")
    res = evaluate_run(raw_dir, gt_path, cfg.condition, metrics_dir)

    assert res["metric_family"] == "point"
    assert "point_metrics" in res and "bbox_metrics" not in res
    assert res["point_metrics"]["point_in_gt_box_acc"]["acc_charged"] == 1.0
    assert res["point_metrics"]["normalized_point_error"]["median_npe"] == 0.0
    # sanity: raw still holds point_2d, never rewritten as a box
    with open(os.path.join(raw_dir, "responses.jsonl"), encoding="utf-8") as fh:
        rec = json.loads(fh.readline())
    assert "point_2d" in rec["raw_response"] and "bbox_2d" not in rec["raw_response"]
