"""VLM-GroundBench deterministic evaluation core (execution layer).

This package implements the LOCKED methodology in docs/ — it does not decide or
reinterpret it. Key invariants enforced here (see docs/metrics_spec.md,
docs/model_matrix.md, docs/benchmark_protocol.md):

    A. Point != bbox.
    B. A point is NEVER scored with IoU.
    C. A point is NEVER converted into a bbox (no coercion).
    D. Ground truth is ALWAYS a bbox.
    E. Cosmos native primitive = point_2d (normalized 0-1000).
    F. Qwen native primitive = bbox (bbox_2d, absolute pixels, xyxy).
    G. Parse failure is tracked separately from localization failure.
    H. Raw outputs are immutable (read-only to the evaluator).
    I. The evaluator is deterministic.
    J. Metric families (BBox / Point) are never merged into one score.

TBD values from docs are NOT filled in here; where a locked decision is missing,
the code raises errors.TBDBlocker instead of inventing a value.
"""
