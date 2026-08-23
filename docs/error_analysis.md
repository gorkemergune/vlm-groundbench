# Error Analysis Plan

> Turns raw errors into understanding. Designed to distinguish **model capability**
> from **prompt effects** (CLAUDE.md Rule #9) and to avoid cherry-picking (Rule #10).
> All qualitative examples are drawn by a documented, seeded sampling procedure.

## Goals

- Characterize *how* models fail at grounding, not just *how often*.
- Attribute errors to sources: model capability, prompt complexity, GT ambiguity,
  or parsing.
- Feed limitations + future-work sections of the report/paper.

## Error taxonomy (proposed, finalized at freeze)

Errors are grouped by the **spatial metric family** they belong to (bbox vs
point — see [`metrics_spec.md`](metrics_spec.md)). **Point-family and BBox/IoU
errors are analyzed within separate families and are never pooled**; there is no
cross-family error code.

### BBox family (Qwen native bbox; all prompt-induced boxes incl. Cosmos-prompted-bbox)

| Code | Category | Description |
|------|----------|-------------|
| **E-LOC** | Localization error | correct object, box too loose/tight/shifted (0 < IoU < τ) |
| **E-WRONG** | Wrong object | confident box on the wrong referent (IoU ≈ 0) |
| **E-HALL** | Hallucination | box for an absent referent (see `metrics_spec.md`) |
| **E-MISS** | Miss | no box / `NOT_PRESENT` for a present referent |
| **E-MULTI** | Multiplicity | wrong number of targets (extra/missing instances) |
| **E-FMT** | Format/parse | output not parseable to a box (tracked separately, per protocol) |
| **E-AMB** | GT ambiguity | expression genuinely ambiguous → not a model fault |

### Point family (Cosmos-native-point only; scored against the GT bbox, never with IoU)

| Code | Category | Description |
|------|----------|-------------|
| **P-IN** (`point_correct` / `point_inside`) | Correct | predicted point falls **inside** the GT box of the correct referent |
| **P-OUT** (`point_outside`) | Outside | correct referent, but the point falls **outside** its GT box |
| **P-WRONG** (`point_wrong_target`) | Wrong target | point lands inside a **different** object's region (wrong referent) |
| **P-HALL** (`point_hallucination`) | Hallucination | point returned for an **absent** referent instead of `NOT_PRESENT` |
| **P-MISS** (`point_missed`) | Miss | no point / `NOT_PRESENT` for a **present** referent |
| **P-DUP** (`point_duplicate`) | Duplicate | redundant/multiple points for a single-target referent |
| **P-FMT** (`point_parse_failure`) | Format/parse | output not parseable to an `(x,y)` point (tracked separately, per protocol) |

- **P-\* codes belong to the Point family and are never combined with E-\* (BBox)
  codes.** IoU is never used to classify a point error; a point is scored only by
  whether it lies inside the GT box (P-IN vs P-OUT/P-WRONG). GT-ambiguity applies
  across both families and is recorded once via E-AMB.
- E-FMT / P-FMT and E-AMB are **not** counted against model capability without a
  flag, to keep capability estimates honest.

## Stratified analysis

Break errors down by:
- **Prompt complexity tier** (L1–L4) → connects to RQ3.
- **Object category / size** (small objects are a known hard case).
- **Scene clutter / number of candidate objects**.
- **Model** and **model family/scale** → connects to RQ2/RQ4.

## Qualitative sampling (anti-cherry-pick)

- Draw a **seeded random sample** of successes and failures per model/tier.
- Also include **worst-case** and **best-case** examples, but **labeled as such**
  and balanced — never presented as typical.
- Record the seed and selection code so the figure set is reproducible.
- Every qualitative figure cites its `sample_id` and links to the raw output.

## Cross-model agreement

- Where do all models fail together (dataset-hard cases vs GT issues)?
- Where do models disagree (capability differences)?
- Confusion patterns between similar objects / expressions.

## Outputs

- Error-taxonomy counts per model/tier → tables + stacked bars in [`../figures/`](../figures).
- A short qualitative gallery (seeded) in [`../report/`](../report).
- A list of GT samples flagged E-AMB for possible annotation review (via the
  annotation protocol — never edited silently).

## Integrity guardrails

- Findings are derived only from `results/` and never by editing raw outputs or
  GT (Rules #1, #4, #6).
- Any claim about *why* a model behaves a certain way is marked as hypothesis
  unless supported by the stratified evidence.
