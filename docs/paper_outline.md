# Paper Outline

> Target: a benchmark/evaluation paper (workshop → conference). This is a
> structural skeleton mapped to the repo's artifacts. Claims about external work
> must be cited (CLAUDE.md Rule #8); model capabilities cited, never invented.

## Working title (placeholder)

*VLM-GroundBench: A Reproducible Benchmark for Natural-Language Visual Grounding
in Vision-Language Models.*

## Abstract (to draft last)

Problem → gap (reproducibility + honest capability vs prompt separation) →
benchmark → key findings across RQ1–RQ5 → takeaway.

## 1. Introduction
- Motivation: grounding as a core VLM capability; why localization matters.
- Gap: inconsistent metrics, unclear capability-vs-prompt attribution,
  irreproducible setups.
- Contributions:
  1. A frozen, model-agnostic grounding protocol with full raw-output provenance.
  2. Evaluation of N VLMs (see `model_matrix.md`) under identical conditions.
  3. Controlled studies of prompt complexity (RQ3) and scale (RQ4).
  4. Accuracy/latency/cost tradeoff analysis (RQ5).
  5. Public, reproducible artifacts.

## 2. Related Work
- Visual grounding / referring expression comprehension. **[cite]**
- VLM evaluation & benchmarks. **[cite]**
- Grounding-specialized models. **[cite]**
- Position relative to prior benchmarks (what's new: reproducibility + protocol
  freeze + capability/prompt separation).

## 3. Benchmark Design
- Task definition; dataset & annotations (`dataset_spec.md`, `annotation_protocol.md`),
  including IAA.
- Frozen protocol (`benchmark_protocol.md`); prompt tiers (`prompt_protocol.md`).
- Metrics with exact definitions (`metrics_spec.md`).
- Reproducibility infrastructure (configs, manifests, env pinning).

## 4. Experimental Setup
- Models + verified capabilities (`model_matrix.md`) — clearly separating verified
  from excluded/unverified.
- Experiments E1/E2 (`experiment_plan.md`); hardware/API conditions; seeds.

## 5. Results
- **5.1 RQ1** cross-model accuracy (IoU/mAP/P/R/F1) with CIs + significance.
- **5.2 RQ2** specialization effect (verified groups only).
- **5.3 RQ3** prompt-complexity sweep.
- **5.4 RQ4** scale within family.
- **5.5 RQ5** accuracy/latency/cost Pareto.

## 6. Error Analysis
- Taxonomy + stratified findings (`error_analysis.md`); seeded qualitative gallery.

## 7. Discussion
- What generalizes; capability vs prompt sensitivity (Rule #9).
- Practical guidance (which model when).

## 8. Limitations
- Dataset size/scope; unverified/excluded models; cross-provider latency/cost
  non-comparability; single-task focus. State honestly (Rule #10).

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
| `dataset_spec.md`, `annotation_protocol.md` | 3 |
| `benchmark_protocol.md`, `prompt_protocol.md`, `metrics_spec.md` | 3, 4 |
| `model_matrix.md` | 4 |
| `experiment_plan.md` | 4, 5 |
| `error_analysis.md` | 6 |
| `results/`, `figures/` | 5, 6 |
