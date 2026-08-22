# Experiment Plan

> Defines the concrete experiments that answer the RQs, each config-driven and
> reproducible (CLAUDE.md Rule #3). Frozen at benchmark freeze.

## Experiment catalog

### E1 — Full-matrix grounding evaluation (RQ1, RQ2, RQ4, RQ5)
- **Vary:** model (all verified models in `model_matrix.md`).
- **Hold constant:** frozen test split, baseline prompt template, decoding params,
  preprocessing, seed.
- **Collect:** raw outputs → IoU, mAP, P/R/F1, hallucination rate, latency, tokens/cost.
- **Analyses:**
  - RQ1: cross-model comparison + significance.
  - RQ2: group by verified grounding-specialization (excluded models omitted).
  - RQ4: same-family scale pairs.
  - RQ5: accuracy vs latency vs cost Pareto frontier.

### E2 — Prompt-complexity sweep (RQ3)
- **Vary:** prompt complexity tier L1→L4 (`prompt_protocol.md`), per model.
- **Hold constant:** images/targets, model, decoding, seed.
- **Collect:** per-tier IoU/F1; within-model deltas across tiers.
- **Report:** prompt sensitivity as distinct from raw capability (Rule #9).

> E1 and E2 share the same frozen inputs and evaluator; only the declared
> variable changes.

## Configuration-driven runs

Every run is defined by a committed config (Rule #3). Proposed schema:

```yaml
run_id: E1_qwen25vl7b_2026-08-22
experiment_id: E1
protocol_version: 1.0.0
model:
  id: qwen2.5-vl-7b
  revision: "<pinned>"        # [⚠ verify]
  access: "<api|local>"       # [⚠ verify]
prompt:
  registry_version: 1.0.0
  prompt_id: grounding.baseline.v1
data:
  split_manifest: data/splits/test_v1.json
  split_hash: "sha256:..."
decoding:
  temperature: 0
  seed: 0
output:
  raw_dir: results/raw_outputs/${run_id}
  metrics_dir: results/metrics/${run_id}
```

- Config + run manifest (see `benchmark_protocol.md`) together fully determine a run.
- Raw outputs and derived metrics are written to separate trees (Rules #4, #5).

## Statistical analysis plan

- **Uncertainty:** 95% bootstrap CIs on all headline metrics.
- **Model comparisons (RQ1/RQ2/RQ4):** paired bootstrap / permutation test over
  shared samples; correct for multiple comparisons (e.g., Holm–Bonferroni).
- **Prompt effect (RQ3):** within-model repeated-measures analysis across tiers.
- **Effect sizes** reported alongside p-values (not p-values alone).
- **Power analysis:** run **before** freeze to set target N (`dataset_spec.md`);
  if power is insufficient, claims are scoped down honestly rather than overstated.

## Execution order

1. Freeze all protocols (see `benchmark_protocol.md` checklist).
2. Verify model access + capabilities (`model_matrix.md`).
3. Dry-run on small dev subset (parsing/format sanity only — not reported).
4. Run E1, then E2. Archive raw outputs immediately.
5. Compute metrics deterministically from raw. Generate figures.
6. Reviewer agent integrity pass (`../agents/reviewer_agent.md`).

## Reproducibility deliverables

- [ ] Committed run configs for every reported run.
- [ ] Pinned environment (lockfile) + `env_hash` in each manifest.
- [ ] Archived raw outputs with checksums.
- [ ] One-command re-computation of all metrics from raw outputs.
