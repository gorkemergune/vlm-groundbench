"""Thin, model-agnostic inference adapters (docs/model_matrix.md).

Contract: predict(image, prompt) -> raw_response (verbatim). Adapters do NO
scoring, NO GT edits, NO coordinate conversion, and NO prompt-content changes.
No real (network/GPU) adapter is implemented in Phase A — only the interface and
an offline DummyAdapter used by tests.
"""
