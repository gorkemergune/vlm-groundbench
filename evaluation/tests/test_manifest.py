"""T-10 — run manifest integrity.

Required fields must be present; TBD fields (returned_model_version) stay None and
are never fabricated (docs/benchmark_protocol.md, docs blocker E).
"""
import pytest

from evaluation.manifest import RunManifest


def _valid_manifest(**overrides):
    base = dict(
        run_id="E1a_qwen_2026-08-24",
        experiment_id="E1a",
        model_id="qwen2.5-vl-7b",
        capability_class="A-bbox",
        condition="Qwen-native-bbox",
        metric_family="bbox",
        prompt_regime="native",
        dataset_role="heldout",
        seed=0,
        split_manifest_hash="sha256:deadbeef",
        code_git_commit="abc1234",
    )
    base.update(overrides)
    return RunManifest(**base)


def test_t10_required_fields_present():
    m = _valid_manifest()
    assert m.missing_required() == []
    m.validate()  # must not raise
    # seed=0 counts as present (checked via `is None`, not falsiness).
    assert m.seed == 0


def test_t10_tbd_field_not_fabricated():
    m = _valid_manifest()
    # returned_model_version is a documented TBD -> stays None, never invented.
    assert m.returned_model_version is None


def test_t10_missing_required_raises():
    m = _valid_manifest(code_git_commit=None)
    assert "code_git_commit" in m.missing_required()
    with pytest.raises(ValueError):
        m.validate()
