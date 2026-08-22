# evaluation/

The deterministic **metric evaluator** lives here (design only — not implemented).

- Reads `results/raw_outputs/`, parses boxes per documented per-model rules,
  computes all metrics in [`../docs/metrics_spec.md`](../docs/metrics_spec.md),
  and writes to `results/metrics/`.
- Deterministic, seeded, re-runnable to **identical** numbers (CLAUDE.md Rule #7).
- **Read-only** with respect to raw outputs and ground truth (Rules #1, #4, #6).
- Applies parsing fairness uniformly; flags parse failures instead of silently
  scoring zero.
