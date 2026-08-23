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

## RQ1 — Tier-A native grounding accuracy

> How accurately can multimodal VLMs perform natural-language visual grounding?

- **Scope:** headline accuracy claims are made for **Tier-A native-grounding
  models** (Qwen2.5-VL-7B, Cosmos3-Nano-Reasoner; see
  [`model_matrix.md`](model_matrix.md)). Tier-C models are reported alongside but
  their coordinates are labeled **prompt-induced**, never native grounding
  (CLAUDE.md Rule #9).
- **Primary evidence:** the **contamination-free custom held-out set** (see
  [`dataset_spec.md`](dataset_spec.md) and [`heldout_spec.md`](heldout_spec.md)).
  Public-benchmark results (RefCOCO/+/g, VG, Flickr30k) are reported **explicitly
  labeled contamination-suspect** and are secondary.
- **H1.0 (null):** Tier-A models achieve statistically indistinguishable mean IoU
  / Acc@0.5 on the held-out set.
- **H1.1 (alt):** At least one Tier-A model differs significantly.
- **Primary metrics:** **Acc@IoU (Acc@0.5, Acc@0.75)** and mean/median IoU
  (see [`metrics_spec.md`](metrics_spec.md)). **mAP is not the primary metric**
  (no comparable confidence scores; task-metric mismatch on single-target REC).
- **Secondary:** Precision/Recall/F1, hallucination rate, parse-success rate.
- **Experiment:** E1a (Tier-A native regime) in [`experiment_plan.md`](experiment_plan.md).
- **Confounds to control:** contamination (→ held-out primary), coordinate
  denormalization per model, prompt regime, image resolution, decoding params.

## RQ2 — Native/documented grounding vs prompt-induced localization

> Does native/documented grounding specialization lead to better localization
> performance than prompt-induced coordinate output?

- **H2.1:** Tier-A models (native/documented bbox output) achieve higher
  **Acc@IoU** than Tier-C models (prompt-induced boxes) on identical inputs.
- **This is a native-vs-prompted contrast, not a flat leaderboard.** A Tier-C
  score conflates localization ability with prompt/format compliance; it is
  reported *with* its parse-success rate and never relabeled as native grounding.
- **Dependency:** the A/C classification in [`model_matrix.md`](model_matrix.md)
  (verified per model).
- **Primary metric:** **Acc@IoU.** Secondary: IoU, hallucination rate,
  parse-success rate. **mAP is NOT used as the primary metric for RQ2.**
- **Experiment:** E1a (A, native regime) vs E1b (all models, shared prompted
  regime), analyzed by tier.
- **Threat to validity:** contamination may inflate Tier-A on public data
  (→ held-out primary); parse failures must be separated from localization
  failures (see [`metrics_spec.md`](metrics_spec.md)).

## RQ3 — Effect of prompt complexity

> How does prompt complexity affect grounding performance?

- **H3.1:** Grounding accuracy varies monotonically (or non-monotonically —
  both are reportable outcomes) with prompt complexity level.
- **Design:** Same images/objects, prompts varied across the frozen complexity
  tiers defined in [`prompt_protocol.md`](prompt_protocol.md) (e.g., L1 bare
  category → L4 relational/attribute-rich referring expression).
- **Metrics:** IoU, F1 per complexity tier; within-model deltas.
- **Experiment:** E2 (prompt-complexity sweep).
- **Cross-model comparability:** RQ3 is evaluated for **all five models**. Because
  each model is its own control across tiers, the *within-model* delta (prompt
  sensitivity) is comparable across all five; the *absolute* per-tier level is
  comparable only within Tier A. Tier-C per-tier accuracy is labeled
  prompt-induced.
- **Integrity note:** Prompts are frozen before results are collected
  (CLAUDE.md Rule #2). This RQ measures *prompt sensitivity*, and per CLAUDE.md
  Rule #9 must be reported as distinct from raw model capability.

## RQ4 — Effect of model scale (Llama 11B vs 90B)

> Does model scale improve grounding/localization performance?

- **H4.1:** Within the Llama 3.2 Vision family, the larger model (90B) yields
  higher Acc@IoU than the smaller (11B) on identical inputs.
- **Design:** the **only** valid controlled scale pair in this benchmark is
  **Llama 3.2 11B (10.6B) vs 90B (88.8B)** — verified same architecture
  (Llama-3.1 backbone + vision adapter), two sizes (see
  [`model_matrix.md`](model_matrix.md)). Both are **Tier C**, so this measures
  *prompt-induced localization* scale, **not** native grounding.
- **Not commensurable → descriptive only:** 7B dense (Qwen) vs 16B MoT (Cosmos)
  vs 30B-A3B MoE (Nemotron, ~3B active) mix architectures/training/regimes; no
  5-point scale curve is drawn.
- **Metrics:** Acc@IoU, IoU vs parameter count (within Llama).
- **Experiment:** E1b restricted to the Llama pair.

## RQ5 — Accuracy / latency / cost tradeoff (dual frontiers)

> What is the tradeoff between localization accuracy, inference latency and
> computational/API cost?

- **H5.1:** No single model dominates on all of {accuracy, latency, cost};
  a Pareto frontier exists.
- **Two separate frontiers, never merged:** **local** {Qwen, Llama 11B, Llama
  90B} vs **NIM-API** {Cosmos, Nemotron}. Cross-frontier latency mixes
  local-GPU with network-served inference and is not a model property.
- **Metrics:** Acc@IoU / F1 vs mean inference latency (p50/p95) vs token usage /
  API cost **where the provider exposes them** (cost may be **TBD** per provider;
  missing values reported N/A, never estimated).
- **Deliverable:** two Pareto plots in [`../figures/`](../figures) + table.
- **Experiment:** E1a/E1b with latency/cost instrumentation, frontier-segregated.

---

## Cross-cutting threat: benchmark contamination

RefCOCO/+/g and Visual Genome are standard grounding-pretraining corpora for
Tier-A models, so public-benchmark scores may reflect memorization rather than
localization. This is a **first-class threat to RQ1 and RQ2**, not a footnote:

- The **custom held-out set is the primary evidence** for the main grounding
  claim (RQ1/RQ2); it is built to be contamination-free (see
  [`heldout_spec.md`](heldout_spec.md), eligibility criteria).
- All public-benchmark numbers are **labeled contamination-suspect** wherever
  reported.
- The **held-out vs public gap** is itself a reported result.

## Traceability matrix

| RQ  | Hypothesis | Primary metric(s)              | Experiment | Valid across | Key confound |
|-----|-----------|---------------------------------|------------|--------------|--------------|
| RQ1 | H1.1      | **Acc@IoU**, IoU (P/R/F1 sec.) | E1a        | Tier A       | contamination, coord denorm |
| RQ2 | H2.1      | **Acc@IoU** (+ parse-success)  | E1a vs E1b | A-vs-C       | parse-vs-loc failure, contamination |
| RQ3 | H3.1      | IoU, F1 per tier (within-model Δ) | E2      | all 5 (Δ)    | prompt freeze |
| RQ4 | H4.1      | Acc@IoU, IoU vs params          | E1b (Llama)| Llama pair   | Tier-C prompt-induced |
| RQ5 | H5.1      | Acc@IoU vs latency vs cost      | E1a/E1b instrumented | within-frontier | local vs API, provider cost data |

> **mAP is not a primary metric for any RQ.** It is reported only on a genuine
> detection subset and only where a model emits usable scores (see
> [`metrics_spec.md`](metrics_spec.md)).

Every reported result must trace back to a row here and to raw outputs under
[`../results/raw_outputs/`](../results/raw_outputs) (CLAUDE.md Rule #7).
