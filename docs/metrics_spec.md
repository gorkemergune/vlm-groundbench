# Metrics Specification

> Exact, unambiguous definitions. "mAP" and "hallucination rate" are ambiguous in
> the literature; here they are pinned down so results are reproducible from raw
> outputs (CLAUDE.md Rule #7). Frozen at benchmark freeze.

## Conventions

- **Box format:** `xywh`, absolute pixels, origin top-left (see `dataset_spec.md`).
- **Prediction:** one or more predicted boxes per (image, expression), possibly
  with a confidence/score if the model provides one (**[⚠ verify per model]** —
  many VLMs do not emit calibrated scores).
- **Matching:** a prediction matches a GT box if `IoU ≥ τ`.

## Core metrics

### IoU (Intersection over Union)
```
IoU(A, B) = area(A ∩ B) / area(A ∪ B)
```
- Reported as **mean IoU** over matched pairs, and as the distribution
  (median, IQR) — not just the mean, to expose skew.

### Precision / Recall / F1 (at threshold τ)
For a fixed IoU threshold τ (default **τ = 0.5**, also report τ = 0.75):
- **TP:** predicted box matches a GT box (IoU ≥ τ), one-to-one (greedy by IoU).
- **FP:** predicted box with no matching GT (includes boxes for `NOT_PRESENT` items).
- **FN:** GT box with no matching prediction (includes missed detections and
  incorrectly returned `NOT_PRESENT`).
- `Precision = TP / (TP + FP)`, `Recall = TP / (TP + FN)`, `F1 = 2PR/(P+R)`.

### mAP (mean Average Precision)
- **Definition used:** COCO-style AP averaged over IoU thresholds
  `0.50:0.05:0.95`, plus `AP@0.5` and `AP@0.75` reported separately.
  **[Assumption — confirm COCO-style is appropriate given single-target
  referring-expression setup]**. Rationale documented at freeze.
- Requires a ranking score. If a model provides none, AP is either (a) computed
  with a constant score (degenerates toward precision/recall at τ) or (b) marked
  **N/A** for that model — the choice is documented and applied uniformly.

### Hallucination rate
- **Definition (v1):** fraction of samples where the model returns a confident
  box for a referent that is **not present** (GT says absent) OR returns a box
  with `IoU = 0` against all GT for a present referent while asserting presence.
  `hallucination_rate = hallucinated_predictions / total_predictions`.
- The `NOT_PRESENT` escape hatch (see `prompt_protocol.md`) is what makes this
  measurable: declining correctly is *not* a hallucination.
- **[Assumption]** exact operationalization finalized at freeze; both the
  "absent-object" and "grossly-wrong-box" components are reported separately.

## Efficiency metrics (RQ5)

- **Mean inference latency:** wall-clock per sample, measured under documented
  conditions (batch size, hardware/endpoint, network for API models). Report
  mean + p50/p95. Cross-provider latency is **not** strictly comparable and is
  labeled as such.
- **Token usage / API cost:** input+output tokens and monetary cost **where the
  provider exposes them** (**[⚠ verify per model/provider]**). Missing values are
  reported as N/A, never estimated silently.

## Aggregation & reporting

- Report per-model and per-prompt-tier breakdowns (RQ3), plus family/scale
  grouping (RQ4) and a Pareto view (RQ5).
- **Uncertainty:** report 95% confidence intervals (bootstrap over samples) for
  headline metrics. Model-vs-model comparisons use an appropriate significance
  test (e.g., bootstrap / paired test over shared samples) — see
  [`experiment_plan.md`](experiment_plan.md).
- **No cherry-picking** (Rule #10): aggregate metrics are primary; qualitative
  examples are seeded samples, not hand-picked wins.

## Edge cases (must be handled explicitly)

| Case | Handling |
|------|----------|
| Multiple predicted boxes | greedy one-to-one match by IoU; extras → FP |
| Multi-target GT | match set-to-set; document |
| Parse failure | flagged; counted per benchmark protocol (not silent 0) |
| Model returns normalized coords | adapter converts before scoring |
| Empty prediction on present object | FN |
| `NOT_PRESENT` on absent object | TN-equivalent / correct decline (not FP) |

## Reproducibility

- Metrics are computed by a single deterministic evaluator over
  `results/raw_outputs/` and written to `results/metrics/`. Re-running must
  reproduce identical numbers (Rule #7). The evaluator never writes to raw
  outputs and never edits GT.
