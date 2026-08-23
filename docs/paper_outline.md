# Paper Outline

> Target: a benchmark/evaluation paper (workshop → conference). This is a
> structural skeleton mapped to the repo's artifacts. Claims about external work
> must be cited (CLAUDE.md Rule #8); model capabilities cited, never invented.

## Working title (placeholder)

*VLM-GroundBench: Native vs Prompt-Induced Visual Grounding — A Reproducible,
Contamination-Aware Benchmark for Vision-Language Models.*

## Abstract (to draft last)

Problem → gap (native grounding conflated with prompt-induced coordinates;
benchmark contamination; irreproducible setups) → our design (native-vs-prompted
framing + contamination-free held-out primary evidence + Acc@IoU) → key findings
across RQ1–RQ5 **[results TBD — placeholders]** → takeaway. **Do not draft
conclusions until results exist.**

## 1. Introduction
- Motivation: grounding as a core VLM capability; why localization matters.
- Gap: (a) benchmarks conflate **native/documented grounding** with
  **prompt-induced coordinate output**; (b) standard grounding datasets are
  **contaminated** into VLM pretraining; (c) inconsistent metrics and
  irreproducible setups.
- Contributions:
  1. A **native-vs-prompted** localization protocol across **three capability
     classes distinguished by native primitive** — **A-bbox** (Qwen2.5-VL-7B,
     native bounding box), **A-point** (Cosmos3-Nano-Reasoner, native `point_2d`;
     **not** native bbox), and **C** prompt-induced (Llama 3.2 11B/90B, Nemotron 3
     Nano Omni) — frozen with full raw-output provenance.
  2. A **contamination-free custom held-out set** as primary evidence, with public
     benchmarks reported as **contamination-suspect**.
  3. **Two non-interchangeable spatial metric families** — **Acc@IoU** (bbox) and
     **point-in-GT-box accuracy** (point); a point is never scored with IoU.
     Parse-success reported separately; mAP restricted to a detection subset,
     never primary.
  4. Controlled studies of **prompt complexity/robustness** (RQ3), **scale**
     (Llama 11B vs 90B, RQ4), and **accuracy/latency/cost** on **separate local
     and NIM-API frontiers** (RQ5).
  5. Public, reproducible artifacts (configs, manifests, raw outputs).

## 2. Related Work
- Visual grounding / referring expression comprehension. **[cite]**
- VLM evaluation & benchmarks. **[cite]**
- Native-grounding VLMs vs general VLMs; what "grounding support" means. **[cite]**
- Benchmark/data contamination in (M)LLMs. **[cite]**
- Position relative to prior benchmarks (what's new: native-vs-prompted separation
  + contamination-free primary evidence + protocol freeze + reproducibility).

## 3. Benchmark Design
- Task definition; **capability classes A-bbox / A-point / C** (`model_matrix.md`).
- Datasets & annotations: **held-out primary** (`heldout_spec.md`) + public
  **contamination-suspect** secondary (`dataset_spec.md`), with IAA
  (`annotation_protocol.md`).
- Frozen protocol (`benchmark_protocol.md`); **two prompt regimes** (native /
  prompted) and complexity tiers (`prompt_protocol.md`).
- Metrics with exact definitions — **two spatial families** (Acc@IoU for bbox;
  point-in-GT-box accuracy for point, never merged), parse-success first-class,
  mAP detection-subset only (`metrics_spec.md`).
- Reproducibility infrastructure (configs, manifests, env pinning, deterministic
  recomputation).

## 4. Experimental Setup
- Models + verified capabilities and **class (A-bbox / A-point / C)**
  (`model_matrix.md`); a prompt-induced coordinate is never reported as native, and
  Cosmos is never reported as native bbox.
- Experiments **E1a** (native — Qwen bbox + **Cosmos-native-point**), **E1b**
  (all-model prompted bbox, incl. **Cosmos-prompted-bbox**), **E2** (prompt
  robustness), **E3** (difficulty), **E4** (hallucination) — (`experiment_plan.md`).
- Hardware/API conditions; **local vs NIM-API** separation; seeds; decoding.

## 5. Results *(all numbers are placeholders until runs complete — do not invent)*
- **5.1 RQ1 — Native localization accuracy (per primitive).** Qwen native **bbox**
  (Acc@0.5/0.75 + IoU) and **Cosmos-native-point** (point-in-GT-box accuracy),
  reported in **separate panels, not merged**, on the **held-out set (primary)**;
  public labeled **contamination-suspect**; held-out-vs-public gap. `[TABLE: TBD] [FIG: TBD]`
- **5.2 RQ2 — Native vs prompt-induced.** (i) bbox contrast: Qwen native bbox vs
  prompt-induced boxes (Cosmos-prompted-bbox, Llama×2, Nemotron), Acc@IoU +
  parse-success; (ii) within-Cosmos: native-point vs prompted-bbox (explicitly
  non-metric-identical). `[TABLE: TBD]`
- **5.3 RQ3 — Prompt complexity & robustness.** Within-model Δ across L1–L4 +
  paraphrase variance, all five. `[FIG: TBD]`
- **5.4 RQ4 — Scale (Llama 11B vs 90B only).** Prompt-induced localization vs
  params; other size differences descriptive only. `[TABLE: TBD]`
- **5.5 RQ5 — Accuracy/latency/cost.** **Two Pareto frontiers** (local vs
  NIM-API); cost N/A where providers don't expose it. `[FIG: TBD ×2]`
- **5.6 Difficulty & hallucination.** E3 per-stratum accuracy (bbox Acc@IoU;
  point-in-GT-box acc / center-distance); E4 `hall_absent`,
  `hall_wrongbox`/`hall_wrongpoint` on negative probes. `[TABLE/FIG: TBD]`

## 6. Error Analysis
- Taxonomy + stratified findings (`error_analysis.md`); seeded qualitative gallery.

## 7. Discussion
- What generalizes; capability vs prompt sensitivity (Rule #9).
- Practical guidance (which model when).

## 8. Limitations
- Held-out set size/scope; residual contamination risk in public results; C-class
  numbers are prompt-induced (not native); **Cosmos native evidence is point-based
  (`point_2d`) — no documented native bbox, so Cosmos bbox results are
  prompt-induced and point vs bbox metrics are not directly comparable**; scale
  claim limited to one Llama pair; cross-provider (local vs NIM-API) latency/cost
  non-comparability; single-task focus; unresolved TBDs (NIM T=0 determinism,
  official pricing). State honestly (Rule #10).

## 9. Reproducibility Statement
- Repo, configs, raw outputs, env, one-command metric recomputation.
- Data licensing + release scope.

## 10. Ethics / Broader Impact (as venue requires)
- Dataset licensing/consent; misuse considerations.

## Appendices
- Full prompt registry; per-model parsing rules; extended tables; extra figures.

---

### Artifact → section map

| Artifact | Feeds section |
|----------|---------------|
| `research_questions.md` | 1, 5 |
| `dataset_spec.md`, `heldout_spec.md`, `annotation_protocol.md` | 3 |
| `benchmark_protocol.md`, `prompt_protocol.md`, `metrics_spec.md` | 3, 4 |
| `model_matrix.md` | 3, 4 |
| `experiment_plan.md` | 4, 5 |
| `error_analysis.md` | 6 |
| `results/`, `figures/` | 5, 6 |
