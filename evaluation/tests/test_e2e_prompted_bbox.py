"""Synthetic E2E for the E1b prompted-bbox regime across all five model bindings,
plus the E1a Cosmos-native-point condition. Offline: DummyAdapter, fabricated raw,
tiny synthetic GT. NO real model/API/data. These are NOT benchmark results.

Verifies:
  - all five prompted-bbox bindings score in the BBox family, is_native=False;
  - Cosmos-prompted-bbox: capability_class == "A-point" BUT metric_family == "bbox"
    and is_native == False (prompt-induced, never native bbox);
  - Cosmos-native-point stays in the Point family (no point->bbox coercion);
  - raw outputs are immutable; derived metrics are written separately.
"""
import hashlib
import json
import os

from evaluation.evaluator import evaluate_run
from evaluation.parsers import PROMPTED_OUTPUT_FORMAT
from experiments.config import RunConfig
from experiments.runner import write_gt, write_raw_run
from models.dummy import DummyAdapter

IMAGE_W, IMAGE_H = 1000, 500
GT_XYWH = [100, 100, 200, 200]  # xyxy [100,100,300,300]; center (200,200)

# The five E1b prompted-bbox bindings: (condition, model_id).
PROMPTED_BINDINGS = [
    ("Qwen-prompted-bbox", "qwen2.5-vl-7b"),
    ("Cosmos-prompted-bbox", "cosmos3-nano-reasoner"),
    ("Llama-11B-prompted-bbox", "llama-3.2-11b-vision"),
    ("Llama-90B-prompted-bbox", "llama-3.2-90b-vision"),
    ("Nemotron-prompted-bbox", "nemotron-3-nano-omni"),
]


def _sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _run(cfg, response, out_root, ofs=None):
    adapter = DummyAdapter(cfg.model_id, {"s1": response})
    samples = [{"sample_id": "s1", "image_w": IMAGE_W, "image_h": IMAGE_H}]
    gt = [{"sample_id": "s1", "referent_present": True, "gt_boxes": [GT_XYWH]}]
    raw_dir = write_raw_run(cfg, adapter, samples, out_root=out_root)
    gt_path = write_gt(gt, os.path.join(out_root, "gt", cfg.condition + ".jsonl"))
    metrics_dir = os.path.join(out_root, "metrics", os.path.basename(raw_dir))
    res = evaluate_run(raw_dir, gt_path, cfg.condition, metrics_dir,
                       output_format_spec=ofs)
    return raw_dir, metrics_dir, res


def test_e2e_five_prompted_bbox_bindings(tmp_path):
    for condition, model_id in PROMPTED_BINDINGS:
        cfg = RunConfig(experiment_id="E1b", model_id=model_id, condition=condition,
                        seed=0, split_manifest=f"synthetic://{condition}",
                        output_format_spec=PROMPTED_OUTPUT_FORMAT)
        out_root = str(tmp_path / condition)
        raw_dir, metrics_dir, res = _run(cfg, {"bbox": [100, 100, 200, 200]},
                                         out_root, ofs=PROMPTED_OUTPUT_FORMAT)
        # scored in the BBox family; prompt-induced (never native)
        assert res["metric_family"] == "bbox"
        assert res["is_native"] is False
        assert "bbox_metrics" in res and "point_metrics" not in res
        assert res["bbox_metrics"]["acc_at_0_5"]["acc_charged"] == 1.0
        assert res["parse_success_rate"] == 1.0
        # raw immutable across evaluation; derived written separately
        resp = os.path.join(raw_dir, "responses.jsonl")
        before = _sha256(resp)
        evaluate_run(raw_dir, os.path.join(out_root, "gt", condition + ".jsonl"),
                     condition, metrics_dir, output_format_spec=PROMPTED_OUTPUT_FORMAT)
        assert _sha256(resp) == before
        assert os.path.exists(os.path.join(metrics_dir, "metrics.json"))
        assert sorted(os.listdir(raw_dir)) == ["manifest.json", "responses.jsonl"]


def test_e2e_cosmos_prompted_vs_native_families(tmp_path):
    # Cosmos-prompted-bbox: model class A-point, but prompt-induced BBox condition.
    cfg_p = RunConfig(experiment_id="E1b", model_id="cosmos3-nano-reasoner",
                      condition="Cosmos-prompted-bbox", seed=0,
                      split_manifest="synthetic://cpb",
                      output_format_spec=PROMPTED_OUTPUT_FORMAT)
    _, _, res_p = _run(cfg_p, {"bbox": [100, 100, 200, 200]},
                       str(tmp_path / "cpb"), ofs=PROMPTED_OUTPUT_FORMAT)
    assert res_p["capability_class"] == "A-point"
    assert res_p["metric_family"] == "bbox"
    assert res_p["is_native"] is False
    assert "bbox_metrics" in res_p and "point_metrics" not in res_p

    # Cosmos-native-point: still the Point family; no point->bbox coercion.
    cfg_n = RunConfig(experiment_id="E1a", model_id="cosmos3-nano-reasoner",
                      condition="Cosmos-native-point", seed=0,
                      split_manifest="synthetic://cnp")
    _, _, res_n = _run(cfg_n, {"point_2d": [200, 400]},  # -> pixel (200,200)
                       str(tmp_path / "cnp"), ofs=None)
    assert res_n["capability_class"] == "A-point"
    assert res_n["metric_family"] == "point"
    assert "point_metrics" in res_n and "bbox_metrics" not in res_n
    assert res_n["point_metrics"]["point_in_gt_box_acc"]["acc_charged"] == 1.0
    # raw still holds point_2d verbatim — never rewritten as a box
    raw_dir = str(tmp_path / "cnp" / "raw_outputs")
    run_dir = os.path.join(raw_dir, os.listdir(raw_dir)[0])
    with open(os.path.join(run_dir, "responses.jsonl"), encoding="utf-8") as fh:
        rec = json.loads(fh.readline())
    assert "point_2d" in rec["raw_response"] and "bbox_2d" not in rec["raw_response"]
