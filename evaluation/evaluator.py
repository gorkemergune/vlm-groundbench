"""Deterministic evaluator (docs/benchmark_protocol.md).

- Read-only with respect to raw outputs and GT (invariant H; Rules #1, #4, #6).
- Deterministic: samples are processed in sorted sample_id order; JSON is written
  with sorted keys (invariant I).
- Dispatches strictly by metric family; never merges families (invariant J).

Phase A scope: scores the NATIVE conditions (Qwen-native-bbox, Cosmos-native-point)
whose coordinate conversions are LOCKED. Scoring prompt-induced bbox conditions
end-to-end needs the frozen prompt output_format_spec (numeric convention), which
is still TBD — so evaluate_records raises TBDBlocker for those rather than guessing.
Parse-success for prompted output is still available via parsers.parse_prompted_bbox.
"""
from __future__ import annotations

import json
import os

from .errors import TBDBlocker
from .families import MetricFamily, Regime, condition_info
from .geometry import BBox, cosmos_norm_point_to_pixel
from .parsers import (
    convert_prompted_numbers,
    parse_cosmos_point,
    parse_prompted_bbox,
    parse_qwen_bbox,
)
from . import metrics as M
from .types import SampleResult


def _build_sample(condition: str, rec: dict, gt: dict,
                  output_format_spec: str | None = None) -> SampleResult:
    info = condition_info(condition)
    family = info["metric_family"]
    referent_present = bool(gt.get("referent_present", True))
    gt_boxes = [BBox(*map(float, b)) for b in gt.get("gt_boxes", [])]

    sr = SampleResult(
        sample_id=str(rec["sample_id"]),
        metric_family=family,
        referent_present=referent_present,
        gt_boxes=gt_boxes,
    )

    raw = rec.get("raw_response")
    if condition == "Qwen-native-bbox":
        pr = parse_qwen_bbox(raw)
        sr.parse_success = pr.success
        sr.pred_bbox = pr.bbox
        sr.not_present = pr.not_present
    elif condition == "Cosmos-native-point":
        pr = parse_cosmos_point(raw)
        sr.parse_success = pr.success
        sr.not_present = pr.not_present
        if pr.success and pr.norm_point is not None:
            nx, ny = pr.norm_point
            sr.pred_point = cosmos_norm_point_to_pixel(
                nx, ny, int(rec["image_w"]), int(rec["image_h"]))
    elif info["regime"] is Regime.PROMPTED and family is MetricFamily.BBOX:
        # Prompted-bbox conditions (incl. Cosmos-prompted-bbox). Coordinates are
        # PROMPT-INDUCED (never native bbox). Scoring requires the locked
        # output_format_spec; without it we do not guess.
        if output_format_spec is None:
            raise TBDBlocker(
                f"Cannot score condition {condition!r}: no output_format_spec was "
                f"provided. The locked prompted-bbox spec must be passed."
            )
        pr = parse_prompted_bbox(raw)
        sr.not_present = pr.not_present
        if pr.not_present:
            sr.parse_success = False            # valid decline, not a parse failure
        elif pr.success:
            bbox = convert_prompted_numbers(pr.raw_numbers, output_format_spec)
            if bbox is None:
                sr.parse_success = False        # invalid box -> parse failure
            else:
                sr.parse_success = True
                sr.pred_bbox = bbox
        else:
            sr.parse_success = False            # unparseable -> parse failure
    else:
        raise KeyError(f"No evaluator wiring for condition {condition!r}")

    # Carry image dimensions through for the Point-family normalized point error
    # (s_i = image diagonal). Harmless for the BBox family.
    sr.image_w = rec.get("image_w")
    sr.image_h = rec.get("image_h")
    return sr


def evaluate_records(condition: str, raw_records: list[dict], gt_records: list[dict],
                     run_info: dict | None = None,
                     output_format_spec: str | None = None) -> dict:
    """Pure, in-memory evaluation. Deterministic given identical inputs."""
    info = condition_info(condition)
    family = info["metric_family"]

    gt_by_id = {str(g["sample_id"]): g for g in gt_records}
    # Deterministic order (invariant I).
    ordered = sorted(raw_records, key=lambda r: str(r["sample_id"]))
    samples = [_build_sample(condition, rec, gt_by_id[str(rec["sample_id"])],
                             output_format_spec=output_format_spec)
               for rec in ordered]

    out: dict = {
        "condition": condition,
        "metric_family": family.value,
        "capability_class": info["capability_class"].value,
        "regime": info["regime"].value,
        "is_native": info["is_native"],
        "n_samples": len(samples),
    }
    if run_info:
        out["run"] = dict(run_info)

    if family is MetricFamily.BBOX:
        out["bbox_metrics"] = {
            "acc_at_0_5": M.acc_at_iou(samples, 0.5),
            "acc_at_0_75": M.acc_at_iou(samples, 0.75),
            "mean_iou": M.mean_iou(samples),
        }
    elif family is MetricFamily.POINT:
        # Invariant J: no bbox Acc@IoU key here; invariant B: no IoU on points.
        out["point_metrics"] = {
            "point_in_gt_box_acc": M.point_in_gt_box_accuracy(samples),  # PRIMARY
            "normalized_point_error": M.normalized_point_error(samples),  # SECONDARY
        }

    out["parse_success_rate"] = M.parse_success_rate(samples)
    out["correct_decline"] = M.correct_decline_rate(samples)  # negative-probe behavior
    out["hallucination"] = M.hallucination(samples)
    return out


def _read_jsonl(path: str) -> list[dict]:
    """Read a .jsonl file READ-ONLY."""
    records = []
    with open(path, "r", encoding="utf-8") as fh:  # 'r' — never opened for writing
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def evaluate_run(raw_dir: str, gt_path: str, condition: str,
                 metrics_dir: str, run_info: dict | None = None,
                 output_format_spec: str | None = None) -> dict:
    """Disk wrapper: read raw (read-only) + GT (read-only), write metrics only.

    Raw outputs under raw_dir are never modified (invariant H).
    """
    raw_records = _read_jsonl(os.path.join(raw_dir, "responses.jsonl"))
    gt_records = _read_jsonl(gt_path)
    result = evaluate_records(condition, raw_records, gt_records, run_info=run_info,
                              output_format_spec=output_format_spec)

    os.makedirs(metrics_dir, exist_ok=True)
    with open(os.path.join(metrics_dir, "metrics.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, sort_keys=True, indent=2)  # deterministic output
    return result
