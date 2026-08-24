"""End-to-end SMOKE test (synthetic, offline).

Proves the pipeline runs: RunConfig -> DummyAdapter -> raw -> parser ->
conversion -> evaluator -> derived metrics -> manifest. Uses fabricated raw
outputs and tiny synthetic GT only. NO real model/data/API. These are NOT
benchmark results.

Asserts the E2E-level invariants requested by the plan:
  1. Qwen native bbox   -> BBox family
  2. Cosmos native point -> Point family
  3. Cosmos point       -> NO bbox conversion
  4. Point              -> NO IoU
  5. Raw output not modified by the evaluator
  6. Manifest has required fields
  7. Same input         -> same derived metrics
  8. TBD fields not fabricated
"""
import hashlib
import json
import os

import pytest

from evaluation.evaluator import evaluate_run
from evaluation.errors import FamilyCoercionError
from evaluation.geometry import BBox, Point, iou
from evaluation.manifest import REQUIRED_FIELDS
from experiments.config import RunConfig
from experiments.runner import write_gt, write_raw_run
from models.dummy import DummyAdapter

# --- synthetic fixtures (W=1000, H=500; GT bbox xyxy [100,100,300,300]) --------
IMAGE_W, IMAGE_H = 1000, 500
GT_XYWH = [100, 100, 200, 200]  # from xyxy [100,100,300,300]

RUN_A = {
    "config": dict(experiment_id="E1a", model_id="qwen2.5-vl-7b",
                   condition="Qwen-native-bbox", seed=0,
                   split_manifest="synthetic://smoke_A"),
    "samples": [{"sample_id": "qa1", "image_w": IMAGE_W, "image_h": IMAGE_H}],
    "responses": {"qa1": {"bbox_2d": [100, 100, 300, 300]}},
    "gt": [{"sample_id": "qa1", "referent_present": True, "gt_boxes": [GT_XYWH]}],
}
RUN_B = {
    "config": dict(experiment_id="E1a", model_id="cosmos3-nano-reasoner",
                   condition="Cosmos-native-point", seed=0,
                   split_manifest="synthetic://smoke_B"),
    "samples": [{"sample_id": "cb1", "image_w": IMAGE_W, "image_h": IMAGE_H}],
    "responses": {"cb1": {"point_2d": [200, 400]}},  # -> pixel (200, 200)
    "gt": [{"sample_id": "cb1", "referent_present": True, "gt_boxes": [GT_XYWH]}],
}


def _sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _run(spec, out_root):
    cfg = RunConfig(**spec["config"])
    adapter = DummyAdapter(cfg.model_id, spec["responses"])
    raw_dir = write_raw_run(cfg, adapter, spec["samples"], out_root=out_root)
    gt_path = write_gt(spec["gt"], os.path.join(out_root, "gt", cfg.condition + ".jsonl"))
    metrics_dir = os.path.join(out_root, "metrics", os.path.basename(raw_dir))
    result = evaluate_run(raw_dir, gt_path, cfg.condition, metrics_dir)
    return raw_dir, metrics_dir, result


def test_e2e_run_a_qwen_bbox_family(tmp_path):
    raw_dir, metrics_dir, res = _run(RUN_A, str(tmp_path))
    # (1) BBox family, and (4) IoU lives only under bbox_metrics
    assert res["metric_family"] == "bbox"
    assert "bbox_metrics" in res and "point_metrics" not in res
    assert res["bbox_metrics"]["acc_at_0_5"]["acc_charged"] == 1.0
    assert res["bbox_metrics"]["mean_iou"] == 1.0
    # (5) raw immutable across evaluation
    resp = os.path.join(raw_dir, "responses.jsonl")
    before = _sha256(resp)
    evaluate_run(raw_dir, os.path.join(str(tmp_path), "gt", "Qwen-native-bbox.jsonl"),
                 "Qwen-native-bbox", metrics_dir)
    assert _sha256(resp) == before
    assert os.path.exists(os.path.join(metrics_dir, "metrics.json"))


def test_e2e_run_b_cosmos_point_family(tmp_path):
    raw_dir, metrics_dir, res = _run(RUN_B, str(tmp_path))
    # (2) Point family; (3)/(4) no bbox metrics, no IoU on the point
    assert res["metric_family"] == "point"
    assert "point_metrics" in res and "bbox_metrics" not in res
    assert res["point_metrics"]["point_in_gt_box_acc"]["acc_charged"] == 1.0
    # (3) raw still holds point_2d verbatim — never rewritten as a box
    with open(os.path.join(raw_dir, "responses.jsonl"), encoding="utf-8") as fh:
        rec = json.loads(fh.readline())
    assert "point_2d" in rec["raw_response"] and "bbox_2d" not in rec["raw_response"]
    # (5) raw immutable
    resp = os.path.join(raw_dir, "responses.jsonl")
    before = _sha256(resp)
    evaluate_run(raw_dir, os.path.join(str(tmp_path), "gt", "Cosmos-native-point.jsonl"),
                 "Cosmos-native-point", metrics_dir)
    assert _sha256(resp) == before


def test_e2e_point_iou_still_forbidden():
    # (4) even at E2E level, computing IoU on a point is a hard error.
    with pytest.raises(FamilyCoercionError):
        iou(Point(200, 200), BBox(*GT_XYWH))


def test_e2e_manifest_required_fields_and_tbd(tmp_path):
    raw_dir, _, _ = _run(RUN_A, str(tmp_path))
    with open(os.path.join(raw_dir, "manifest.json"), encoding="utf-8") as fh:
        manifest = json.load(fh)
    # (6) required fields present and non-None
    for field in REQUIRED_FIELDS:
        assert manifest.get(field) is not None, f"missing required field {field}"
    # methodology-critical fields carried through
    assert manifest["capability_class"] == "A-bbox"
    assert manifest["metric_family"] == "bbox"
    assert manifest["prompt_regime"] == "native"
    # (8) TBD field not fabricated
    assert manifest["returned_model_version"] is None


def test_e2e_determinism(tmp_path):
    # (7) same synthetic input -> identical derived metrics
    _, _, res1 = _run(RUN_A, str(tmp_path / "run1"))
    _, _, res2 = _run(RUN_A, str(tmp_path / "run2"))
    assert json.dumps(res1, sort_keys=True) == json.dumps(res2, sort_keys=True)
