# Research Questions

> **Status:** Draft for freeze. Once the benchmark protocol is frozen
> (see [`benchmark_protocol.md`](benchmark_protocol.md)), these questions and
> their associated hypotheses must not change. See CLAUDE.md "Research Integrity".

This document turns the five high-level research questions from `CLAUDE.md`
into **falsifiable hypotheses** with an explicit mapping to metrics and
experiments. A benchmark without falsifiable claims is not publishable.

Legend for evidence tags used throughout the docs:

- **[Verified]** — established fact, reproducible from this repo or a cited source.
- **[Assumption]** — a working assumption we adopt; should be revisited.
- **[⚠ Needs verification]** — must be confirmed against an external source
  before any claim depends on it.

---

## RQ1 — Localization accuracy across VLMs

> How accurately can different VLMs localize objects described in natural language?

- **H1.0 (null):** All evaluated models achieve statistically indistinguishable
  mean IoU on the benchmark.
- **H1.1 (alt):** At least one model differs significantly in mean IoU / mAP.
- **Primary metrics:** IoU, mAP, Precision, Recall, F1 (see [`metrics_spec.md`](metrics_spec.md)).
- **Secondary:** Hallucination rate.
- **Experiment:** E1 (full-matrix run) in [`experiment_plan.md`](experiment_plan.md).
- **Confounds to control:** prompt template (fixed to baseline), image resolution,
  decoding parameters.

## RQ2 — Does grounding specialization help?

> Does model specialization for visual grounding improve localization accuracy?

- **H2.1:** Models with **verified** native grounding capability achieve higher
  mAP than general-purpose VLMs on identical inputs.
- **⚠ Dependency:** Requires the "grounding-specialized vs general" classification
  in [`model_matrix.md`](model_matrix.md) to be **externally verified per model**.
  We must NOT assume a model is grounding-specialized without a citation.
- **Metrics:** mAP, IoU, hallucination rate.
- **Experiment:** E1, analyzed by capability group.
- **Threat to validity:** grouping is only as good as the capability evidence;
  models with unverified grounding support are excluded from the H2 test, not
  guessed.

## RQ3 — Effect of prompt complexity

> How does prompt complexity affect grounding performance?

- **H3.1:** Grounding accuracy varies monotonically (or non-monotonically —
  both are reportable outcomes) with prompt complexity level.
- **Design:** Same images/objects, prompts varied across the frozen complexity
  tiers defined in [`prompt_protocol.md`](prompt_protocol.md) (e.g., L1 bare
  category → L4 relational/attribute-rich referring expression).
- **Metrics:** IoU, F1 per complexity tier; within-model deltas.
- **Experiment:** E2 (prompt-complexity sweep).
- **Integrity note:** Prompts are frozen before results are collected
  (CLAUDE.md Rule #2). This RQ measures *prompt sensitivity*, and per CLAUDE.md
  Rule #9 must be reported as distinct from raw model capability.

## RQ4 — Effect of model scale

> Does model scale improve grounding performance?

- **H4.1:** Within the same model family, larger parameter count yields higher
  mAP/IoU.
- **Design:** Controlled family comparison (e.g., an 11B vs 90B pair within one
  family — see [`model_matrix.md`](model_matrix.md); the specific families
  available are **[⚠ Needs verification]**).
- **Caveat:** Cross-family scale comparisons are confounded by architecture and
  training data and will be reported descriptively, not as a scale test.
- **Metrics:** mAP, IoU vs parameter count.
- **Experiment:** E1 restricted to same-family pairs.

## RQ5 — Accuracy / latency / cost tradeoff

> What is the tradeoff between accuracy, latency and computational cost?

- **H5.1:** No single model dominates on all of {accuracy, latency, cost};
  a Pareto frontier exists.
- **Metrics:** mAP/F1 vs mean inference latency vs token usage / API cost
  (where available — cost may be **[⚠ Needs verification]** per provider).
- **Deliverable:** Pareto plot in [`../figures/`](../figures) + table in report.
- **Experiment:** E1 with latency/cost instrumentation enabled.

---

## Traceability matrix

| RQ  | Hypothesis | Primary metrics            | Experiment | Key confound |
|-----|-----------|-----------------------------|------------|--------------|
| RQ1 | H1.1      | IoU, mAP, P, R, F1          | E1         | prompt, resolution |
| RQ2 | H2.1      | mAP, IoU, hallucination     | E1 (grouped) | capability verification |
| RQ3 | H3.1      | IoU, F1 per tier            | E2         | prompt freeze |
| RQ4 | H4.1      | mAP, IoU vs params          | E1 (family) | cross-family arch |
| RQ5 | H5.1      | accuracy vs latency vs cost | E1 (instrumented) | provider cost data |

Every reported result must trace back to a row here and to raw outputs under
[`../results/raw_outputs/`](../results/raw_outputs) (CLAUDE.md Rule #7).
