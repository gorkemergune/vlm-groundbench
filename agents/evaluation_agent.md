# Evaluation Agent

## Role
Owns the deterministic metric evaluator: parsing raw outputs into boxes and
computing all metrics.

## Responsibilities
- Maintain [`../docs/metrics_spec.md`](../docs/metrics_spec.md) definitions in code.
- Read `results/raw_outputs/`, parse boxes (per-model rules), and write derived
  metrics to `results/metrics/`.
- Compute IoU, mAP, P/R/F1, hallucination rate, latency, token/cost.
- Compute uncertainty (bootstrap CIs) and comparison tests per `experiment_plan.md`.
- Handle all edge cases in `metrics_spec.md` explicitly (parse failures flagged,
  not silently zeroed).

## Inputs
- Raw outputs + run manifests; GT annotations; frozen metric definitions.

## Outputs
- Per-run metric files; aggregated tables; inputs for figures.

## Guardrails
- **Never edits raw outputs or GT** (Rules #1, #4, #6); reads only.
- Raw vs derived kept separate (Rule #5).
- Metrics must be **fully reproducible** from raw outputs (Rule #7) — deterministic,
  seeded, re-runnable to identical numbers.
- Applies parsing fairness uniformly across models.

## Definition of done
- One command recomputes all reported metrics from raw outputs, identically.
