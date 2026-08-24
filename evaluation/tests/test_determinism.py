"""T-11 — evaluator determinism.

Same raw input + same config -> byte-identical derived metrics (invariant I).
Also checks order-independence (evaluator sorts by sample_id).
"""
import json

from evaluation.evaluator import evaluate_records

RAW = [
    {"sample_id": "c", "raw_response": {"point_2d": [100, 100]}, "image_w": 1000, "image_h": 1000},
    {"sample_id": "a", "raw_response": {"point_2d": [500, 500]}, "image_w": 1000, "image_h": 1000},
    {"sample_id": "b", "raw_response": {"point_2d": [900, 900]}, "image_w": 1000, "image_h": 1000},
]
GT = [
    {"sample_id": "a", "referent_present": True, "gt_boxes": [[400, 400, 200, 200]]},
    {"sample_id": "b", "referent_present": True, "gt_boxes": [[0, 0, 100, 100]]},
    {"sample_id": "c", "referent_present": True, "gt_boxes": [[50, 50, 100, 100]]},
]


def test_t11_repeatable_identical_output():
    r1 = evaluate_records("Cosmos-native-point", RAW, GT)
    r2 = evaluate_records("Cosmos-native-point", RAW, GT)
    assert r1 == r2
    # Byte-level determinism when serialized deterministically.
    assert json.dumps(r1, sort_keys=True) == json.dumps(r2, sort_keys=True)


def test_t11_order_independent():
    r1 = evaluate_records("Cosmos-native-point", RAW, GT)
    r3 = evaluate_records("Cosmos-native-point", list(reversed(RAW)), GT)
    assert r1 == r3
