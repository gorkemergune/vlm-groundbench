# Annotation Protocol

> Applies whether we adopt existing annotations (verification pass) or create a
> hand-curated control set. Enforces CLAUDE.md Rule #1 (never auto-modify GT)
> and Rule #6 (never manually alter evaluation results).

## Objectives

- Produce/verify **bounding-box ground truth** paired with **natural-language
  referring expressions**, at a quality high enough that model errors are
  attributable to models, not to noisy GT.
- Assign each sample a **prompt complexity tier** (L1–L4) consistent with
  [`prompt_protocol.md`](prompt_protocol.md) — this drives RQ3.

## Annotation unit

One annotation = (image, referring expression, one-or-more GT boxes, tier, notes).
A referring expression should ideally resolve to a **single** target region
unless the sample is explicitly a multi-instance case (flagged).

## Guidelines (to be finalized before annotation starts)

1. **Box tightness:** smallest axis-aligned box fully containing the referent.
2. **Occlusion:** annotate the visible + amodal extent per a documented choice
   (record the choice; be consistent).
3. **Ambiguity:** if an expression matches >1 region, either (a) rewrite the
   expression to disambiguate, or (b) mark as multi-target — never silently pick one.
4. **Complexity tiering:** assign L1–L4 using the rubric in `prompt_protocol.md`.
5. **Language:** expressions are natural, grammatical, and self-contained (no
   reliance on external context).

## Quality control

- **Inter-annotator agreement (IAA):** ≥2 annotators on an overlap subset
  (target overlap ≥ 20% of samples). Report:
  - Box agreement via mean pairwise IoU.
  - Tier-label agreement via Cohen's / Fleiss' κ.
- **Adjudication:** disagreements resolved by a third reviewer; decision logged.
- **Acceptance threshold:** define a minimum IAA (e.g., mean IoU ≥ 0.7, κ ≥ 0.6)
  **[Assumption — thresholds to be confirmed at freeze]**; samples below threshold
  are fixed or dropped, not shipped noisy.

## Versioning & immutability

- Annotations are stored under `data/annotations/` as immutable, versioned files.
- Any correction creates a **new version** with a changelog entry (who, when,
  why) — the previous version is retained. No in-place silent edits (Rule #1).
- A `data/annotations/CHANGELOG.md` records every change post-freeze.

## Tooling

- Any labeling tool is acceptable; the **export must conform** to the GT schema
  in [`dataset_spec.md`](dataset_spec.md).
- Automated pre-labeling (if ever used) must be **human-verified**; model-proposed
  boxes are never accepted as GT without review, and never for models under
  evaluation (to avoid circularity).

## Deliverables

- [ ] Final annotation guidelines doc (this file, frozen).
- [ ] IAA report with κ and IoU on the overlap subset.
- [ ] Versioned annotation files + manifest.
