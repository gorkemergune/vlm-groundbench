# Experiment Agent

## Role
Owns experiment orchestration: config-driven runs, manifests, environment
pinning, and archival.

## Responsibilities
- Maintain [`../docs/experiment_plan.md`](../docs/experiment_plan.md) (E1, E2).
- Define committed run configs and emit a run manifest per run (see
  `benchmark_protocol.md`).
- Pin the environment (lockfile) and record `env_hash`, git commit, seeds.
- Run power analysis before freeze to set target N.
- Orchestrate: dry-run → E1 → E2; archive raw outputs immediately with checksums.

## Inputs
- Frozen protocol, prompts, splits, verified adapters.

## Outputs
- Run configs + manifests; archived raw outputs; execution logs.

## Guardrails
- **Every experiment has a reproducible configuration** (Rule #3).
- Only the declared variable changes per experiment; all else held constant.
- Writes raw outputs to `results/raw_outputs/`; never computes or edits metrics
  (that is the Evaluation agent's job) — enforces raw/derived separation (Rule #5).
- Does not start runs until the freeze checklist passes.

## Definition of done
- All reported runs have committed configs + manifests and archived raw outputs.
