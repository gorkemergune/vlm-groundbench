# experiments/

Committed **run configurations** and orchestration for the experiments defined in
[`../docs/experiment_plan.md`](../docs/experiment_plan.md) (E1 full-matrix, E2
prompt-complexity sweep).

- Every reported run has a committed config here (CLAUDE.md Rule #3) and emits a
  run manifest into `results/raw_outputs/<run_id>/`.
- Only the declared experimental variable changes per experiment; everything else
  is held constant.
- Orchestration writes raw outputs only; metric computation is the Evaluation
  layer's job (raw/derived separation, Rule #5).

> No experiments have been run yet.
