"""T-12 — raw/derived separation.

The evaluator reads raw outputs read-only and writes ONLY derived metrics
(invariant H; Rules #4/#6). Raw files must be byte-identical after a run.
"""
import hashlib
import json
import os

from evaluation.evaluator import evaluate_run


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


def test_t12_raw_outputs_are_immutable(tmp_path):
    raw_dir = tmp_path / "raw_outputs" / "E1a_qwen_run"
    raw_dir.mkdir(parents=True)
    responses = raw_dir / "responses.jsonl"
    responses.write_text(
        json.dumps({"sample_id": "a", "raw_response": {"bbox_2d": [0, 0, 10, 10]}}) + "\n",
        encoding="utf-8",
    )
    manifest = raw_dir / "manifest.json"
    manifest.write_text(json.dumps({"run_id": "E1a_qwen_run"}), encoding="utf-8")

    gt_path = tmp_path / "annotations.jsonl"
    gt_path.write_text(
        json.dumps({"sample_id": "a", "referent_present": True,
                    "gt_boxes": [[0, 0, 10, 10]]}) + "\n",
        encoding="utf-8",
    )

    metrics_dir = tmp_path / "metrics" / "E1a_qwen_run"

    before = {p: _sha256(p) for p in (str(responses), str(manifest))}
    result = evaluate_run(str(raw_dir), str(gt_path), "Qwen-native-bbox", str(metrics_dir))
    after = {p: _sha256(p) for p in (str(responses), str(manifest))}

    # Raw files unchanged (immutable).
    assert before == after
    # Derived metrics written separately, and are non-trivial.
    metrics_file = metrics_dir / "metrics.json"
    assert metrics_file.exists()
    assert result["metric_family"] == "bbox"
    # Evaluator did not create anything new inside the raw dir.
    assert sorted(os.listdir(raw_dir)) == ["manifest.json", "responses.jsonl"]
