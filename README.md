# VLM-GroundBench

A **reproducible, model-agnostic benchmark** for evaluating vision-language
models (VLMs) on **natural-language visual grounding** — localizing objects in
images from free-text descriptions — with rigorous metrics, frozen protocols,
and full raw-output provenance.

> **Status:** Design/specification phase. No datasets downloaded, no model
> adapters implemented, no experiments run. The methodology is being frozen
> before any evaluation, per the project's research-integrity rules.

## Research questions

| RQ  | Question |
|-----|----------|
| RQ1 | How accurately can different VLMs localize objects described in natural language? |
| RQ2 | Does model specialization for visual grounding improve localization accuracy? |
| RQ3 | How does prompt complexity affect grounding performance? |
| RQ4 | Does model scale improve grounding performance? |
| RQ5 | What is the accuracy / latency / cost tradeoff? |

See [`docs/research_questions.md`](docs/research_questions.md) for hypotheses and
the metric/experiment traceability matrix.

## Repository layout

```
docs/         # research design & frozen protocols (start here)
agents/       # role charters for the multi-agent research workflow
models/       # thin inference adapters (design only, not implemented)
evaluation/   # deterministic metric evaluator (design only)
experiments/  # committed run configs & orchestration (E1, E2)
data/         # raw / processed / annotations / splits (GT is immutable)
results/      # raw_outputs (verbatim) + metrics (derived) — kept separate
figures/      # reproducible figures from results
report/       # paper draft (docs/paper_outline.md)
```

## Documentation index

| Doc | Purpose |
|-----|---------|
| [project_scope.md](docs/project_scope.md) | In/out of scope, success criteria, risks |
| [research_questions.md](docs/research_questions.md) | RQs → hypotheses → metrics → experiments |
| [dataset_spec.md](docs/dataset_spec.md) | Dataset requirements, candidates, schema, splits |
| [annotation_protocol.md](docs/annotation_protocol.md) | GT guidelines, tiering, IAA |
| [benchmark_protocol.md](docs/benchmark_protocol.md) | **The freeze document** — pipeline & manifests |
| [prompt_protocol.md](docs/prompt_protocol.md) | Versioned prompts, complexity tiers (RQ3) |
| [metrics_spec.md](docs/metrics_spec.md) | Exact metric definitions |
| [model_matrix.md](docs/model_matrix.md) | Models + capability verification (nothing invented) |
| [experiment_plan.md](docs/experiment_plan.md) | E1/E2, configs, statistics, power |
| [error_analysis.md](docs/error_analysis.md) | Error taxonomy & anti-cherry-pick sampling |
| [paper_outline.md](docs/paper_outline.md) | Paper structure → artifact map |

## Reproducibility & integrity principles

- Frozen protocol + versioned prompts + pinned environment.
- Raw model outputs saved verbatim and separated from derived metrics.
- All headline metrics recomputable from raw outputs by a third party.
- Ground-truth annotations are never modified automatically.
- Model capabilities are **verified and cited, never invented**; unverified
  capabilities are excluded from dependent claims.

See `CLAUDE.md` for the full integrity rules.

## License

Apache-2.0 (see `LICENSE`).
