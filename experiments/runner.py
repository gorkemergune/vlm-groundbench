"""Synthetic end-to-end runner (OFFLINE smoke only).

Wires the pipeline together with a DummyAdapter and fabricated raw outputs:

    RunConfig -> Adapter -> raw_outputs (verbatim) -> manifest
                                        |
                                        v
                       evaluator (parse -> convert -> metrics) -> derived metrics

This produces NO benchmark results — only proof that the execution pipeline runs
on synthetic data. It never downloads models/data and never calls an API.

Manifest fields that are legitimately computable (git commit, env hash, split
hash) are computed for real. Fields that are TBD in docs/ (returned_model_version)
stay None and are NEVER fabricated.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

from evaluation.manifest import RunManifest
from experiments.config import RunConfig
from models.base import Adapter

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def git_commit() -> str | None:
    """Real HEAD commit, or None if git is unavailable (never fabricated)."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=_REPO_ROOT,
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip() or None
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None


def env_hash() -> str:
    """Deterministic fingerprint of the runtime environment (real, reproducible)."""
    parts = [sys.version]
    req = os.path.join(_REPO_ROOT, "requirements.txt")
    if os.path.exists(req):
        with open(req, "r", encoding="utf-8") as fh:
            parts.append(fh.read())
    return _sha256_text("\n".join(parts))


def split_manifest_hash(samples: list[dict]) -> str:
    """Real content hash of the (synthetic) frozen input set."""
    canonical = json.dumps(
        [{"sample_id": s["sample_id"], "image_w": s["image_w"], "image_h": s["image_h"]}
         for s in sorted(samples, key=lambda s: str(s["sample_id"]))],
        sort_keys=True,
    )
    return "sha256:" + _sha256_text(canonical)


def default_run_id(config: RunConfig) -> str:
    safe = config.condition.replace("/", "_")
    return f"{config.experiment_id}_{config.model_id}_{safe}".replace(" ", "_")


def build_manifest(config: RunConfig, samples: list[dict], run_id: str) -> RunManifest:
    m = RunManifest(
        run_id=run_id,
        experiment_id=config.experiment_id,
        model_id=config.model_id,
        capability_class=config.capability_class.value,
        condition=config.condition,
        metric_family=config.metric_family.value,
        prompt_regime=config.prompt_regime.value,
        dataset_role=config.dataset_role,
        contamination_suspect=config.contamination_suspect,
        seed=config.seed,
        split_manifest_hash=split_manifest_hash(samples),
        code_git_commit=git_commit(),
        env_hash="sha256:" + env_hash(),
        decoding_params=dict(config.decoding),
        prompt_registry_version=config.prompt_registry_version,
        returned_model_version=None,   # TBD: no real NIM call -> never fabricated
        timestamp_utc=None,            # left None for a deterministic smoke run
    )
    m.validate()
    return m


def write_raw_run(config: RunConfig, adapter: Adapter, samples: list[dict],
                  out_root: str, run_id: str | None = None) -> str:
    """Produce raw outputs + manifest (the ADAPTER side). No scoring here.

    Returns the raw_dir. The adapter response is stored VERBATIM.
    """
    config.validate()
    run_id = run_id or default_run_id(config)
    raw_dir = os.path.join(out_root, "raw_outputs", run_id)
    os.makedirs(raw_dir, exist_ok=True)

    raw_records = []
    for s in sorted(samples, key=lambda s: str(s["sample_id"])):
        # NOTE: prompt content is a SMOKE placeholder. Real benchmark prompts are
        # frozen in the (still TBD) prompt registry; DummyAdapter ignores content.
        raw = adapter.predict(s["sample_id"], s.get("prompt", "<SMOKE_PROMPT>"))
        raw_records.append({
            "sample_id": s["sample_id"],
            "raw_response": raw,           # verbatim
            "image_w": s["image_w"],
            "image_h": s["image_h"],
        })

    with open(os.path.join(raw_dir, "responses.jsonl"), "w", encoding="utf-8") as fh:
        for r in raw_records:
            fh.write(json.dumps(r, sort_keys=True) + "\n")

    manifest = build_manifest(config, samples, run_id)
    with open(os.path.join(raw_dir, "manifest.json"), "w", encoding="utf-8") as fh:
        fh.write(manifest.to_json())

    return raw_dir


def write_gt(gt_records: list[dict], path: str) -> str:
    """Write the (synthetic) GT fixture. GT is ALWAYS bbox (invariant D)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for g in sorted(gt_records, key=lambda g: str(g["sample_id"])):
            fh.write(json.dumps(g, sort_keys=True) + "\n")
    return path
