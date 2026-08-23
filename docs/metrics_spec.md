# Metrics Specification

> Exact, unambiguous definitions. "mAP" and "hallucination rate" are ambiguous in
> the literature; here they are pinned down so results are reproducible from raw
> outputs (CLAUDE.md Rule #7). Frozen at benchmark freeze.

## Conventions

- **Two canonical schemas, one per spatial family:**
  - **BBox family** → `xywh`, absolute pixels, origin top-left.
  - **Point family** → `(x, y)`, absolute pixels, origin top-left.
  Every prediction is converted to the schema of **its** family by the evaluation
  adapter (per-condition rules in [`model_matrix.md`](model_matrix.md)),
  **unit-tested** before any reported run.
- **Prediction:** one or more predicted boxes **or** points per (image,
  expression), depending on the condition. A confidence/score is used **only if
  the model natively provides one** (**[⚠ verify per model]**; none of the five is
  known to emit calibrated, comparable scores).
- **Output labels preserved in all reporting:** every prediction carries (a) its
  **primitive** (bbox | point), (b) its **condition** (e.g. `Qwen-native-bbox`,
  `Cosmos-native-point`, `Cosmos-prompted-bbox`, `Llama-prompted-bbox`), and (c)
  whether it is **native** or **prompt-induced**. A prompt-induced coordinate is
  never described as native. **Cosmos is never labeled native bbox.**

## Two spatial evaluation families (do NOT merge)

Bounding-box predictions and point predictions measure different things and are
scored by **different, non-interchangeable** metric families. **A point prediction
is never scored with IoU**, and box vs point numbers are **not** reported as
directly equivalent.

- **Family A — BBox localization** (Qwen native bbox; all prompt-induced boxes,
  incl. Cosmos-prompted-bbox): IoU, **Acc@IoU (primary)**, parse-success,
  duplicate/matching rules.
- **Family B — Point localization** (Cosmos-native-point): **point-in-GT-box
  accuracy (primary)**, normalized point error / center-distance, parse-success.

Cross-family comparison (e.g. Cosmos-native-point vs Qwen native bbox) is
presented as **two separate results**, explicitly labeled non-equivalent — never a
single combined ranking.

## Family A — BBox localization metrics

### IoU (Intersection over Union)
For axis-aligned boxes `A, B`:
```
IoU(A, B) = area(A ∩ B) / area(A ∪ B),   with area(A ∪ B) = area(A)+area(B)−area(A ∩ B)
```
- Reported as **mean IoU** and as the distribution (median, IQR) — not the mean
  alone, to expose skew. IoU = 0 for disjoint boxes.

### Acc@IoU — PRIMARY metric for the BBox family (RQ1 bbox, RQ2 bbox, RQ4)
The **primary** accuracy metric for single-target bounding-box grounding.
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
- Reported **per model, per condition** (bbox family). It is never folded into IoU
  or Acc@IoU. For prompt-induced conditions this separates "cannot format a box"
  from "cannot localize" — essential to the RQ2 native-vs-prompted claim.
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

## Family B — Point localization metrics

Used for **Cosmos-native-point** predictions (documented `point_2d`, converted to
`(x,y)` abs-px). **IoU is never computed on a point.**

### Point-in-GT-box accuracy — PRIMARY metric for the Point family (RQ1 point, RQ2 point)
For `N` single-target samples with a predicted point `p_i = (x,y)` and the GT box
`gt_i`:
```
PointAcc = (1/N) · Σ_i  1[ p_i ∈ gt_i ]
```
`p_i ∈ gt_i` iff the point lies inside (or on) the GT bounding box. Parse-failed
samples handled with the same dual basis (charged vs excluded) as Acc@IoU.

### Normalized point error / center-distance (secondary)
For samples where the point is expected near the referent center, report the
Euclidean point-to-GT-center distance normalized by a documented scale:
```
NPE_i = || p_i − center(gt_i) ||_2  /  s_i
```
where `s_i` is a fixed normalization scale — **choice TBD at freeze** (candidates:
image diagonal, or √(GT box area)); the chosen `s_i` is documented and applied
uniformly. Report median NPE + distribution. Also report raw center-distance in
pixels for the small-object stratum (see `heldout_spec.md`, E3), since point
localization is size-robust in a way IoU is not.

### Parse-success rate (Point family)
```
point_parse_success = (# samples whose raw output yields ≥1 valid point) / (total samples)
```
A "valid point" = parseable to `(x,y)` inside image bounds. Reported separately;
never folded into PointAcc. **Point parse-success and BBox parse-success are
reported under their own families, not pooled.**

> **Non-equivalence rule:** PointAcc and Acc@IoU are **not** directly comparable
> and are never averaged, ranked together, or presented as the same axis.

### Hallucination rate
Requires **negative probes** (referent genuinely absent), which public REC data
lacks — supplied by the held-out set ([`heldout_spec.md`](heldout_spec.md)). Two
components, reported **separately** (not summed into one opaque number):
- **Absent-object hallucination:** on a negative-probe sample (GT = absent), the
  model returns a box instead of `NOT_PRESENT`.
  ```
  hall_absent = (# negative-probe samples with a returned box) / (# negative-probe samples)
  ```
- **Gross-wrong (present referent):**
  - *BBox family:* on a present referent the model asserts presence and returns a
    box with `IoU = 0` against all GT.
    ```
    hall_wrongbox = (# present samples with asserted box, IoU=0 vs all GT) / (# present samples with an asserted box)
    ```
  - *Point family (Cosmos-native-point):* the model returns a point that lies
    **outside all** GT boxes.
    ```
    hall_wrongpoint = (# present samples with asserted point ∉ any GT box) / (# present samples with an asserted point)
    ```
- `hall_absent` applies to both families (a returned box **or** point instead of
  `NOT_PRESENT`). Box and point hallucination components are reported under their
  own families, not pooled.
- Correctly returning `NOT_PRESENT` on an absent referent is **not** a
  hallucination (it is a correct decline). Parse failures are excluded from all
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
- Every accuracy figure carries its **primitive** (bbox | point), its **condition
  label** (native vs prompt-induced), and its **parse-failure basis** (charged vs
  excluded). BBox (Acc@IoU) and Point (PointAcc) results are reported in separate
  columns/panels — never merged into one score.
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
| Model returns normalized/native coords | adapter converts to the **family's** canonical schema before scoring |
| Box out of image bounds | clamp to image; if area collapses to 0 → parse failure |
| **Point prediction (Cosmos-native-point)** | scored with **Family B** (PointAcc / NPE); **never IoU**; never converted to a box |
| **Point out of image bounds** | clamp; if still invalid → point parse failure |
| **Box expected but a point returned (or vice versa)** | scored only in the family matching the **condition**; cross-family coercion is prohibited |
| Empty prediction on present object | FN / miss (in the relevant family) |
| `NOT_PRESENT` on absent object (negative probe) | correct decline (not FP, not hallucination) |
| `NOT_PRESENT` on present object | FN + counts toward miss, not hallucination |

## Reproducibility

- Metrics are computed by a single deterministic evaluator over
  `results/raw_outputs/` and written to `results/metrics/`. Re-running must
  reproduce identical numbers (Rule #7). The evaluator never writes to raw
  outputs and never edits GT.
