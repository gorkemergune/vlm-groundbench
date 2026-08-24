"""Prompt registry + prompted-bbox parser/converter/evaluator integration.

output_format_spec = LOCKED "xywh_abs_pixels" (Karar B): {"bbox": [x,y,w,h]} abs-px.
New tests only; existing tests untouched. No real model/API/data.
"""
import pytest

from evaluation.errors import TBDBlocker
from evaluation.evaluator import evaluate_records
from evaluation.geometry import BBox
from evaluation.parsers import (
    PROMPTED_OUTPUT_FORMAT,
    convert_prompted_numbers,
    parse_prompted_bbox,
)
from experiments.config import RunConfig
from experiments.prompt_registry import (
    load_registry,
    output_format_id,
    prompted_bbox_entry,
)


# --- registry --------------------------------------------------------------
def test_registry_loads_and_locks_format():
    reg = load_registry()
    assert output_format_id(reg) == PROMPTED_OUTPUT_FORMAT == "xywh_abs_pixels"
    e = prompted_bbox_entry(reg)
    assert set(e["applies_to"]) == {
        "qwen2.5-vl-7b", "cosmos3-nano-reasoner",
        "llama-3.2-11b-vision", "llama-3.2-90b-vision", "nemotron-3-nano-omni",
    }
    assert '"bbox"' in e["text_template"] and "NOT_PRESENT" in e["text_template"]
    assert reg["output_format_spec"]["json_key"] == "bbox"
    assert reg["output_format_spec"]["order"] == "x,y,w,h"


# --- parser + converter ----------------------------------------------------
def test_parse_prompted_accepts_bbox_key():
    pr = parse_prompted_bbox({"bbox": [10, 20, 30, 40]})
    assert pr.success is True and pr.raw_numbers == [10, 20, 30, 40]


def test_convert_identity_and_invalid():
    # xywh abs-px IS canonical -> identity map
    assert convert_prompted_numbers([10, 20, 30, 40], PROMPTED_OUTPUT_FORMAT) == BBox(10, 20, 30, 40)
    # invalid box (w<=0) -> None (evaluator will record a PARSE FAILURE)
    assert convert_prompted_numbers([10, 20, 0, 40], PROMPTED_OUTPUT_FORMAT) is None
    assert convert_prompted_numbers([10, 20, 30], PROMPTED_OUTPUT_FORMAT) is None


def test_convert_unknown_spec_blocks():
    with pytest.raises(TBDBlocker):
        convert_prompted_numbers([1, 2, 3, 4], "normalized_0_1000")


# --- config validation -----------------------------------------------------
def test_config_prompted_requires_locked_spec():
    base = dict(experiment_id="E1b", model_id="llama-3.2-11b-vision",
                condition="Llama-11B-prompted-bbox", seed=0, split_manifest="x")
    with pytest.raises(ValueError):
        RunConfig(**base).validate()                      # no output_format_spec
    RunConfig(**base, output_format_spec=PROMPTED_OUTPUT_FORMAT).validate()  # ok


# --- evaluator integration -------------------------------------------------
def _raw(bbox_val, sid="a"):
    return [{"sample_id": sid, "raw_response": {"bbox": bbox_val}}]


def _gt(box, sid="a", present=True):
    return [{"sample_id": sid, "referent_present": present, "gt_boxes": [box]}]


def test_prompted_bbox_scored_bbox_family_not_native():
    res = evaluate_records("Qwen-prompted-bbox", _raw([100, 100, 200, 200]),
                           _gt([100, 100, 200, 200]),
                           output_format_spec=PROMPTED_OUTPUT_FORMAT)
    assert res["metric_family"] == "bbox" and res["is_native"] is False
    assert "point_metrics" not in res
    assert res["bbox_metrics"]["acc_at_0_5"]["acc_charged"] == 1.0
    assert res["parse_success_rate"] == 1.0


def test_cosmos_prompted_bbox_is_prompt_induced_bbox():
    res = evaluate_records("Cosmos-prompted-bbox", _raw([100, 100, 200, 200]),
                           _gt([100, 100, 200, 200]),
                           output_format_spec=PROMPTED_OUTPUT_FORMAT)
    # model class stays A-point, but this condition is prompt-induced BBox
    assert res["capability_class"] == "A-point"
    assert res["metric_family"] == "bbox" and res["is_native"] is False
    assert "bbox_metrics" in res and "point_metrics" not in res


def test_prompted_parse_success_excludes_decline():
    raw = [
        {"sample_id": "a", "raw_response": {"bbox": [100, 100, 200, 200]}},  # valid
        {"sample_id": "b", "raw_response": "I cannot find it"},              # parse-fail
        {"sample_id": "c", "raw_response": "NOT_PRESENT"},                   # decline
    ]
    gt = [
        {"sample_id": "a", "referent_present": True, "gt_boxes": [[100, 100, 200, 200]]},
        {"sample_id": "b", "referent_present": True, "gt_boxes": [[0, 0, 10, 10]]},
        {"sample_id": "c", "referent_present": True, "gt_boxes": [[0, 0, 10, 10]]},
    ]
    res = evaluate_records("Llama-11B-prompted-bbox", raw, gt,
                           output_format_spec=PROMPTED_OUTPUT_FORMAT)
    # population = {a, b} (c declined -> excluded); success = {a} -> 0.5
    assert res["parse_success_rate"] == 0.5


def test_prompted_without_spec_blocks():
    with pytest.raises(TBDBlocker):
        evaluate_records("Llama-11B-prompted-bbox", _raw([1, 1, 2, 2]),
                         _gt([1, 1, 2, 2]))  # no output_format_spec
