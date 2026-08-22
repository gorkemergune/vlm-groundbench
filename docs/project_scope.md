# Project Scope

## One-line summary

A reproducible, model-agnostic benchmark for evaluating vision-language models
(VLMs) on **natural-language visual grounding** — localizing objects in images
from free-text descriptions — with rigorous metrics, frozen protocols, and full
raw-output provenance.

## In scope

- **Task:** Referring-expression grounding / open-vocabulary object localization,
  output as bounding boxes. (Segmentation masks are out of scope for v1.)
- **Evaluation** of the models listed in [`model_matrix.md`](model_matrix.md)
  under a **single frozen protocol**.
- **Controlled studies** of prompt complexity (RQ3) and model scale (RQ4).
- **Efficiency profiling:** latency and token/cost accounting (RQ5).
- **Reproducibility infrastructure:** config-driven runs, environment pinning,
  raw-output archival, deterministic metric recomputation.

## Out of scope (v1)

- Training or fine-tuning any model (evaluation-only benchmark).
- Segmentation, keypoints, 3D grounding, video grounding.
- Building a new large-scale dataset from scratch (we curate/adopt an existing
  annotated source or a small hand-annotated set — see [`dataset_spec.md`](dataset_spec.md)).
- Human preference / subjective quality studies.
- Real-time / on-device deployment engineering.

## Success criteria

**As a research artifact**
- Every headline number is reproducible from raw outputs by a third party
  (CLAUDE.md Rule #7).
- Frozen protocol + versioned prompts + pinned environment.
- Clear separation of model capability vs prompt engineering (Rule #9).

**As a portfolio / CV project**
- Clean repo, readable README, figures that tell the story at a glance.
- Documented methodology that demonstrates research maturity.

**As a paper**
- Falsifiable hypotheses (see [`research_questions.md`](research_questions.md)).
- Statistical treatment of comparisons (significance, confidence intervals).
- Honest error analysis and stated limitations.

## Non-goals / explicit stances

- We do **not** claim to rank "the best VLM" in general — only grounding under
  this protocol.
- We do **not** invent or infer model capabilities; unverified capabilities are
  flagged and excluded from capability-dependent claims.
- We do **not** cherry-pick qualitative examples (Rule #10); qualitative figures
  are sampled by a documented, seeded procedure.

## Stakeholders / roles

The work is organized around specialized agent roles (see [`../agents/`](../agents)):
Research, Dataset, Annotation, Model, Evaluation, Experiment, Reviewer.
The human **Research Director** owns protocol freeze and integrity sign-off.

## Key risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Model grounding capability unverified | RQ2/RQ4 invalid | Verify per model; exclude unverified from those claims |
| Dataset licensing unclear | Cannot publish | Resolve licensing in `dataset_spec.md` before any download |
| Prompt/format bias favors some models | Unfair comparison | Report per-prompt-tier; document parsing fairness |
| API cost/latency non-comparable across providers | RQ5 muddy | Normalize + document measurement conditions |
| Small dataset → low statistical power | Weak claims | Power analysis before freeze; report CIs |
