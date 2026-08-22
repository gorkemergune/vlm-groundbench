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

| Code | Category | Description |
|------|----------|-------------|
| **E-LOC** | Localization error | correct object, box too loose/tight/shifted (0 < IoU < τ) |
| **E-WRONG** | Wrong object | confident box on the wrong referent (IoU ≈ 0) |
| **E-HALL** | Hallucination | box for an absent referent (see `metrics_spec.md`) |
| **E-MISS** | Miss | no box / `NOT_PRESENT` for a present referent |
| **E-MULTI** | Multiplicity | wrong number of targets (extra/missing instances) |
| **E-FMT** | Format/parse | output not parseable to a box (tracked separately, per protocol) |
| **E-AMB** | GT ambiguity | expression genuinely ambiguous → not a model fault |

- E-FMT and E-AMB are **not** counted against model capability without a flag,
  to keep capability estimates honest.

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
