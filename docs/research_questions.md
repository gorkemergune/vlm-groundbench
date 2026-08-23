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

## RQ1 — Native localization accuracy (by primitive)

> How accurately can multimodal VLMs perform natural-language visual grounding?

- **Scope:** headline accuracy claims are made for the **native/documented
  localization** conditions, reported **per spatial primitive on its own metric
  family** (see [`model_matrix.md`](model_matrix.md), [`metrics_spec.md`](metrics_spec.md)):
  - **Native bounding box** — Qwen2.5-VL-7B → **BBox family** (Acc@IoU).
  - **Native point** — Cosmos3-Nano-Reasoner (`point_2d`) → **Point family**
    (point-in-GT-box accuracy). **Cosmos is not a native-bbox model.**
  These two are **not combined into one ranking** (different primitive, different
  metric family, non-equivalent). Prompt-induced conditions are reported alongside
  and labeled *prompt-induced*, never native.
- **Primary evidence:** the **contamination-free custom held-out set** (see
  [`dataset_spec.md`](dataset_spec.md), [`heldout_spec.md`](heldout_spec.md)).
  Public benchmarks (RefCOCO/+/g, VG, Flickr30k) are reported **labeled
  contamination-suspect** and are secondary.
- **H1.0 (null):** within a metric family, native conditions are statistically
  indistinguishable on the held-out set.
- **H1.1 (alt):** at least one native condition differs significantly (assessed
  **within** a family, not across families).
- **Primary metrics:** **Acc@IoU (0.5, 0.75)** for bbox; **point-in-GT-box
  accuracy** for point. **mAP is not primary.**
- **Secondary:** IoU / normalized point error, P/R/F1, hallucination, parse-success.
- **Experiment:** E1a (native regime — Qwen native bbox + **Cosmos-native-point**).
- **Confounds:** contamination (→ held-out primary), per-condition coordinate
  conversion, prompt regime, resolution, decoding.

## RQ2 — Native/documented localization vs prompt-induced localization

> Does native/documented localization lead to better performance than
> prompt-induced coordinate output?

- **Two contrasts, kept separate (never merged across primitive):**
  - **H2.1 (bbox family):** Qwen **native bbox** achieves higher **Acc@IoU** than
    **prompt-induced boxes** (Cosmos-prompted-bbox, Llama 11B/90B, Nemotron) on
    identical inputs.
  - **H2.2 (within-Cosmos):** **Cosmos-native-point** localizes its target better
    (point-in-GT-box accuracy) than **Cosmos-prompted-bbox** does (Acc@IoU) —
    reported as a within-model native-vs-prompted comparison, with the explicit
    caveat that point and bbox metrics are **not directly equivalent** (the
    comparison is *native primitive vs prompted primitive within one model*, not a
    metric-identical test).
- **Not a flat leaderboard.** A prompt-induced score conflates localization with
  format compliance; it is reported *with* its parse-success rate and never
  relabeled native.
- **Dependency:** the A-bbox / A-point / C classification in
  [`model_matrix.md`](model_matrix.md).
- **Primary metric:** **Acc@IoU** (bbox contrast); **point-in-GT-box accuracy**
  (point side). **mAP is NOT primary for RQ2.**
- **Experiment:** E1a (native conditions) vs E1b (all models, shared prompted-bbox
  regime — includes **Cosmos-prompted-bbox**).
- **Threat to validity:** contamination may inflate native conditions on public
  data (→ held-out primary); parse failures separated from localization failures;
  point vs bbox never presented as the same axis.

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
  each model is its own control across complexity tiers, the *within-model* delta
  (prompt sensitivity) is comparable across all five; the *absolute* per-tier level
  is comparable only **within a shared metric family** (bbox Acc@IoU among the bbox
  conditions; point-in-GT-box acc for Cosmos-native-point separately). Prompt-
  induced per-tier accuracy is labeled prompt-induced.
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
| RQ1 | H1.1      | **Acc@IoU** (bbox: Qwen); **point-in-GT-box acc** (point: Cosmos) — per family, not merged | E1a | native bbox / native point (separately) | contamination, coord conversion, primitive non-equivalence |
| RQ2 | H2.1 (bbox), H2.2 (within-Cosmos) | **Acc@IoU** (bbox contrast) + parse-success; **point-in-GT-box acc** (point side) | E1a vs E1b | Qwen-native-bbox vs prompt-induced bbox; Cosmos native-point vs prompted-bbox | parse-vs-loc failure, contamination, point↔bbox non-equivalence |
| RQ3 | H3.1      | IoU, F1 per tier (within-model Δ) | E2      | all 5 (Δ)    | prompt freeze |
| RQ4 | H4.1      | Acc@IoU, IoU vs params          | E1b (Llama)| Llama pair   | Tier-C prompt-induced |
| RQ5 | H5.1      | Acc@IoU vs latency vs cost      | E1a/E1b instrumented | within-frontier | local vs API, provider cost data |
| RQ1 | —         | per stratum: Acc@IoU (Qwen bbox); point-in-GT-box acc / center-dist (Cosmos point) | **E3** | native (acc, per family) + all 5 (behavior) | small-box IoU instability (report center-distance) |
| RQ1/RQ2 | —     | `hall_absent`, `hall_wrongbox`  | **E4**     | all 5        | needs held-out negative probes |

> **E3** (difficulty-stratified grounding) and **E4** (hallucination / negative
> probes) provide **secondary characterization/evidence** for RQ1 (and RQ2 for
> E4); they do not alter the RQ definitions or their primary hypotheses.

> **mAP is not a primary metric for any RQ.** It is reported only on a genuine
> detection subset and only where a model emits usable scores (see
> [`metrics_spec.md`](metrics_spec.md)).

Every reported result must trace back to a row here and to raw outputs under
[`../results/raw_outputs/`](../results/raw_outputs) (CLAUDE.md Rule #7).
