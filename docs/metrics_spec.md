# Metrics Specification

> Exact, unambiguous definitions. "mAP" and "hallucination rate" are ambiguous in
> the literature; here they are pinned down so results are reproducible from raw
> outputs (CLAUDE.md Rule #7). Frozen at benchmark freeze.

## Conventions

- **Canonical box format:** `xywh`, absolute pixels, origin top-left (see
  `dataset_spec.md`). Every model's raw output is converted to this by the
  evaluation adapter (per-model rules in [`model_matrix.md`](model_matrix.md)),
  **unit-tested against known boxes** before any reported run.
- **Prediction:** one or more predicted boxes per (image, expression). A
  confidence/score is used **only if the model natively provides one**
  (**[⚠ verify per model]**; none of the five is known to emit calibrated,
  comparable scores).
- **Matching:** a prediction matches a GT box if `IoU ≥ τ`.
- **Output tier label:** every predicted box carries its regime — **native**
  (Tier-A) or **prompt-induced** (Tier-C) — and this label is preserved in all
  reporting. A prompt-induced box is never described as native grounding.

## Core metrics

### IoU (Intersection over Union)
For axis-aligned boxes `A, B`:
```
IoU(A, B) = area(A ∩ B) / area(A ∪ B),   with area(A ∪ B) = area(A)+area(B)−area(A ∩ B)
```
- Reported as **mean IoU** and as the distribution (median, IQR) — not the mean
  alone, to expose skew. IoU = 0 for disjoint boxes.

### Acc@IoU — PRIMARY metric (RQ1, RQ2, RQ4)
The **primary** accuracy metric for single-target referring-expression grounding.
For a set of `N` single-target samples and threshold τ:
```
Acc@τ = (1/N) · Σ_i  1[ IoU(pred_i*, gt_i) ≥ τ ]
```
where `pred_i*` is the model's **selected** box for sample `i` (see selection
rule under *Duplicate objects & multiple predictions*), and `1[·]` is the
indicator. Report **Acc@0.5** and **Acc@0.75**.
- **Parse-failed** samples: `IoU` is undefined. Acc@τ is reported **two ways**:
  (a) *parse-failure = incorrect* (charged to the model), and (b) *parse-failure
  excluded* (localization-only) — both, always, so format ability and
  localization ability are separable (RQ2 integrity). The denominator basis is
  stated in every table.

### Precision / Recall / F1 (at threshold τ, for multi-target / detection cases)
For a fixed IoU threshold τ (default **τ = 0.5**, also report τ = 0.75), used for
multi-target grounding (Flickr30k Entities, VG) and hallucination accounting:
- **TP:** predicted box matched one-to-one to a GT box with IoU ≥ τ.
- **FP:** predicted box with no matching GT (includes boxes emitted for a
  `NOT_PRESENT`/absent referent).
- **FN:** GT box with no matching prediction (includes misses and incorrectly
  returned `NOT_PRESENT` on a present referent).
- `Precision = TP / (TP + FP)`, `Recall = TP / (TP + FN)`, `F1 = 2PR/(P+R)`.

### Parse-success rate — FIRST-CLASS metric
```
parse_success_rate = (# samples whose raw output yields ≥1 valid box) / (total samples)
```
- Reported **per model, per regime, per tier**. It is never folded into IoU or
  Acc@IoU. For Tier-C models this separates "cannot format a box" from "cannot
  localize" — essential to the RQ2 native-vs-prompted claim.
- A "valid box" = parseable to canonical `xywh` with `w>0, h>0` inside image
  bounds (after clamping policy below).

### mAP (secondary, restricted — NOT a primary metric anywhere)
- mAP is **not** used for the single-target REC accuracy claims (no comparable
  confidence scores; task-metric mismatch). It is computed **only** on a genuine
  **detection subset** (VG/Flickr multi-object) and **only** for a model that
  natively emits usable ranking scores; otherwise **N/A** for that model.
- When computed: COCO-style AP over IoU `0.50:0.05:0.95`, plus `AP@0.5`/`AP@0.75`.
- A constant-score fallback is **not** used to manufacture an mAP (it degenerates
  to precision/recall and would be misleading). Absence of scores → N/A, reported
  as such.

### Hallucination rate
Requires **negative probes** (referent genuinely absent), which public REC data
lacks — supplied by the held-out set ([`heldout_spec.md`](heldout_spec.md)). Two
components, reported **separately** (not summed into one opaque number):
- **Absent-object hallucination:** on a negative-probe sample (GT = absent), the
  model returns a box instead of `NOT_PRESENT`.
  ```
  hall_absent = (# negative-probe samples with a returned box) / (# negative-probe samples)
  ```
- **Gross-wrong-box (present referent):** on a present referent the model asserts
  presence and returns a box with `IoU = 0` against all GT.
  ```
  hall_wrongbox = (# present samples with asserted box, IoU=0 vs all GT) / (# present samples with an asserted box)
  ```
- Correctly returning `NOT_PRESENT` on an absent referent is **not** a
  hallucination (it is a correct decline). Parse failures are excluded from both
  numerators and reported via parse-success instead.

## Efficiency metrics (RQ5)

- **Mean inference latency:** wall-clock per sample, measured under documented
  conditions (batch size, hardware/endpoint, network for API models). Report
  mean + p50/p95. Cross-provider latency is **not** strictly comparable and is
  labeled as such.
- **Token usage / API cost:** input+output tokens and monetary cost **where the
  provider exposes them** (**[⚠ verify per model/provider]**). Missing values are
  reported as N/A, never estimated silently.

## Aggregation & reporting

- **Primary basis** for the main grounding claim (RQ1/RQ2) is the
  **contamination-free held-out set**; public-benchmark numbers are reported
  **labeled contamination-suspect**.
- Every accuracy figure carries its **tier label** (native vs prompt-induced) and
  its **parse-failure basis** (charged vs excluded).
- Report per-model and per-prompt-tier breakdowns (RQ3), the Llama-pair scale
  comparison (RQ4), and **two** Pareto views — local vs NIM-API (RQ5).
- **Uncertainty:** report 95% confidence intervals (bootstrap over samples) for
  headline metrics. Model-vs-model comparisons use an appropriate significance
  test (e.g., bootstrap / paired test over shared samples) — see
  [`experiment_plan.md`](experiment_plan.md).
- **No cherry-picking** (Rule #10): aggregate metrics are primary; qualitative
  examples are seeded samples, not hand-picked wins.

## Duplicate objects & multiple predictions (explicit rules)

- **Single-target sample, multiple predicted boxes (Acc@IoU):** the model's
  `pred*` is the **first** box it emits (primary), and — as a documented secondary
  — the **best-IoU** box (oracle-selection upper bound). Both are reported; the
  first-box number is the headline (no oracle peeking in the primary claim). Extra
  boxes are ignored for Acc@IoU but counted as FP in the P/R/F1 view.
- **Duplicate/near-identical predictions:** deduplicate predictions with
  pairwise `IoU ≥ 0.95` before matching (documented; applied uniformly).
- **Multi-target sample (detection view):** one-to-one assignment by **Hungarian
  matching** maximizing total IoU subject to `IoU ≥ τ`; unmatched predictions →
  FP, unmatched GT → FN. (Greedy-by-IoU may be reported as a documented
  alternative but Hungarian is canonical for multi-target.)
- **Duplicate GT objects** (genuinely identical referents): the sample is flagged
  multi-target in annotation; set-to-set matching applies. A single-target
  expression that matches >1 region is resolved in annotation, never silently.

## Parse-failure counting (explicit)

- A sample is **parse-failed** if the raw output yields **zero** valid boxes and
  is **not** a valid `NOT_PRESENT` decline.
- Parse failures are (a) counted in `parse_success_rate`, (b) reported as their
  own row in the error taxonomy (E-FMT, `error_analysis.md`), and (c) surfaced in
  Acc@τ under **both** the "parse-failure = incorrect" and "parse-failure
  excluded" bases. They are never silently scored 0 without the flag.

## Edge cases (must be handled explicitly)

| Case | Handling |
|------|----------|
| Multiple predicted boxes (single target) | headline = first box; secondary = best-IoU; extras → FP in P/R/F1 |
| Duplicate predictions (IoU ≥ 0.95) | deduplicated before matching |
| Multi-target GT | Hungarian one-to-one, IoU ≥ τ; unmatched pred→FP, GT→FN |
| Parse failure | flagged; in parse-success + both Acc bases (never silent 0) |
| Model returns normalized/native coords | adapter converts to canonical `xywh` abs-px before scoring |
| Box out of image bounds | clamp to image; if area collapses to 0 → parse failure |
| Empty prediction on present object | FN (localization miss) |
| `NOT_PRESENT` on absent object (negative probe) | correct decline (not FP, not hallucination) |
| `NOT_PRESENT` on present object | FN + counts toward miss, not hallucination |

## Reproducibility

- Metrics are computed by a single deterministic evaluator over
  `results/raw_outputs/` and written to `results/metrics/`. Re-running must
  reproduce identical numbers (Rule #7). The evaluator never writes to raw
  outputs and never edits GT.
