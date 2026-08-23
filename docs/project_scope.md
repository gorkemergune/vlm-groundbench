# Project Scope

## One-line summary

A reproducible benchmark for evaluating vision-language models (VLMs) on
**natural-language visual grounding** — localizing objects in images from
free-text descriptions — framed as a **native-vs-prompted study**: it separates
**Tier-A native/documented grounding** (Qwen2.5-VL-7B, Cosmos3-Nano-Reasoner)
from **Tier-C prompt-induced** coordinate output (Llama 3.2 11B/90B Vision,
Nemotron 3 Nano Omni). Rigorous metrics, frozen protocols, full raw-output
provenance. The **primary evidence** for the main grounding claim is a
**contamination-free held-out set**; public benchmarks are reported as
contamination-suspect.

## In scope

- **Task:** Referring-expression grounding / open-vocabulary object localization,
  output as bounding boxes. (Segmentation masks are out of scope for v1.)
- **Evaluation** of the models in [`model_matrix.md`](model_matrix.md) under a
  frozen protocol with **two prompt regimes** (native for Tier A, prompted for
  all) — see [`prompt_protocol.md`](prompt_protocol.md).
- **A contamination-free held-out set** (primary evidence) plus contamination-
  suspect public benchmarks — see [`dataset_spec.md`](dataset_spec.md) and
  [`heldout_spec.md`](heldout_spec.md).
- **Controlled studies** of prompt complexity (RQ3, all five) and model scale
  (RQ4, **Llama 11B vs 90B only**).
- **Efficiency profiling:** latency and token/cost accounting on **two frontiers**
  (local vs NIM-API) (RQ5).
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
- We do **not** put Tier-A native output and Tier-C prompt-induced output on one
  grounding leaderboard; a prompt-induced coordinate is **never** described as
  native grounding (CLAUDE.md Rule #9).
- We do **not** treat public-benchmark scores as clean capability evidence; they
  are contamination-suspect, and the held-out set is primary.
- We do **not** invent or infer model capabilities, dataset sizes, contamination
  rates, or licenses; unknowns are marked TBD / needing verification.
- We do **not** cherry-pick qualitative examples (Rule #10); qualitative figures
  are sampled by a documented, seeded procedure.

## Stakeholders / roles

The work is organized around specialized agent roles (see [`../agents/`](../agents)):
Research, Dataset, Annotation, Model, Evaluation, Experiment, Reviewer.
The human **Research Director** owns protocol freeze and integrity sign-off.

## Key risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **Output-contract asymmetry** (A native bbox vs C prompt-induced) | Apples-to-oranges leaderboard | Native-vs-prompted framing; tier labels on every number; parse-success reported separately |
| **Benchmark contamination** (RefCOCO/VG in Tier-A pretraining) | RQ1/RQ2 inflated | Held-out set as primary evidence; public labeled contamination-suspect; report the gap |
| Coordinate-format mismatch (Qwen abs-px vs Cosmos 0–1000) | Silent IoU bugs | Per-model denorm in adapter, unit-tested before any reported run |
| Prompt/format bias favors some models | Unfair comparison | Two documented regimes; per-tier reporting; robust parser |
| API cost/latency non-comparable across providers | RQ5 muddy | **Two frontiers** (local vs NIM-API); document measurement conditions |
| API non-determinism / version drift (NIM) | Non-reproducible | Pin endpoint version; capture returned model version per call; [⚠ verify T=0] |
| Small held-out set → low power | Weak Tier-A claim | Per-tier power analysis before freeze; report CIs |
| Dataset licensing unclear | Cannot publish | Resolve in `dataset_spec.md`; Flickr30k reference-only; ship IDs+scripts not images |
