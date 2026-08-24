# Annotation Protocol

> Applies to (1) **adopted public/source annotations** (verification pass only),
> (2) the **custom held-out set** we create, and (3) **negative probes** within
> that held-out set. Enforces CLAUDE.md Rule #1 (never auto-modify GT) and Rule #6
> (never manually alter evaluation results). Aligns with
> [`heldout_spec.md`](heldout_spec.md) and [`dataset_spec.md`](dataset_spec.md).

## Three annotation classes (must be distinguished)

| Class | `dataset_role` | `contamination_suspect` | What we do |
|-------|----------------|-------------------------|------------|
| **Source/public** (RefCOCO/+/g, VG, Flickr30k) | `public_secondary` | **true** | **Verify only** — spot-check box quality + tier assignment; never rewrite the source GT. Used as contamination-suspect secondary evidence. |
| **Custom held-out (positive)** | `heldout` | **false** | **Author + annotate** fresh expressions and boxes (primary evidence). |
| **Negative probe** (held-out) | `heldout` | **false** | Author an expression for a **plausibly-expected-but-absent** object; **no GT box**; `referent_present=false`. |

> Source annotations are treated as immutable inputs; any suspected error is
> logged for review, **not** edited (Rule #1). Only custom held-out samples are
> authored by us.

## Schema fields this protocol is responsible for

Consistent with the GT schema in [`dataset_spec.md`](dataset_spec.md), each sample
carries:

- **`referent_present`** — `true` for positive samples (≥1 GT box); `false` for
  negative probes (no GT box; correct model behavior = `NOT_PRESENT`).
- **`dataset_role`** — `heldout` (primary) or `public_secondary`.
- **`contamination_suspect`** — `false` for held-out, `true` for public.
- **`prompt_complexity_tier`** — L1–L4 (rubric in
  [`prompt_protocol.md`](prompt_protocol.md)); drives RQ3.
- **`is_multi_target`** — flagged when the referent legitimately resolves to >1
  region.
- **`difficulty`** — `{size_bin, occluded, clutter}` (definitions + thresholds in
  [`heldout_spec.md`](heldout_spec.md); thresholds **TBD at freeze**).

## Objectives

- Produce (held-out) / verify (public) **bounding-box ground truth** paired with
  **natural-language referring expressions**, at a quality high enough that model
  errors are attributable to models, not to noisy GT.
- Assign each sample its complexity tier and (for held-out) difficulty labels.

## Annotation unit

One annotation = (image, referring expression, zero-or-more GT boxes,
`referent_present`, tier, difficulty, role flags, notes). A referring expression
resolves to a **single** target unless explicitly `is_multi_target` (flagged).
**Negative probes carry zero GT boxes** by construction.

> **No separate point GT.** The canonical annotation is the object/referent
> **bounding box** plus the existing metadata — for **all** models, including
> Cosmos. Annotators do **not** annotate a point target. Cosmos-native-point
> predictions are scored against the GT **box** (point-in-GT-box), so no additional
> annotation task is introduced (see [`heldout_spec.md`](heldout_spec.md),
> [`dataset_spec.md`](dataset_spec.md)).

## Guidelines (to be finalized before annotation starts)

1. **Box tightness:** smallest axis-aligned box fully containing the referent.
2. **Occlusion:** annotate the visible + amodal extent per a documented choice
   (record the choice; be consistent). Occlusion also drives the `occluded`
   difficulty label.
3. **Ambiguity / duplicates:** if an expression matches >1 region, either (a)
   rewrite the expression to disambiguate, or (b) mark `is_multi_target=true` with
   **all** GT boxes — never silently pick one. Genuinely duplicated/identical
   referents are captured as multi-target; scoring then uses set-to-set Hungarian
   matching, and multiple *predicted* boxes are handled per
   [`metrics_spec.md`](metrics_spec.md) (headline = first box; secondary =
   best-IoU; dedup at IoU ≥ 0.95). Annotators do **not** score.
4. **Complexity tiering:** assign L1–L4 using the rubric in `prompt_protocol.md`.
5. **Difficulty labels (held-out):** assign `size_bin`, `occluded`, `clutter` per
   [`heldout_spec.md`](heldout_spec.md).
6. **Negative probes (held-out):** the named object must be **plausibly expected
   but genuinely absent** (not absurd/out-of-domain); set `referent_present=false`
   and leave GT boxes empty. Match to positive samples where feasible.
7. **Language:** expressions are natural, grammatical, and self-contained; each
   positive target carries **≥2 frozen paraphrases** of equal complexity for the
   RQ3 robustness probe.

## Quality control

- **Inter-annotator agreement (IAA):** ≥2 annotators on an overlap subset
  (target overlap ≥ 20% of samples). Report:
  - Box agreement via mean pairwise IoU (positive samples).
  - Tier-label and **difficulty-label** agreement via Cohen's / Fleiss' κ.
  - **Negative-probe agreement:** agreement on `referent_present` (the object is
    genuinely absent) via κ — a negative probe is invalid if annotators disagree
    on absence.
- **Adjudication:** disagreements resolved by a third reviewer; decision logged in
  `data/annotations/CHANGELOG.md`.
- **Acceptance criteria (LOCKED) — annotation / held-out data-quality gates, NOT
  model-performance thresholds:**
  - box agreement: **mean pairwise IoU ≥ 0.70**
  - capability/tier agreement: **κ ≥ 0.60**
  - difficulty agreement: **κ ≥ 0.60**
  - negative-probe agreement (`referent_present`): **κ ≥ 0.60**

  These gate GROUND-TRUTH quality only; they say nothing about model accuracy.
  Samples below threshold are fixed or dropped, **never shipped noisy**. This
  applies to held-out samples; public samples failing verification are
  flagged/excluded, not edited.

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
- [ ] IAA report with κ and IoU on the overlap subset (incl. difficulty +
      negative-probe agreement).
- [ ] Versioned annotation files + manifest, with `dataset_role` /
      `contamination_suspect` / `referent_present` populated per sample.
- [ ] Held-out positive/negative balance + difficulty distribution recorded
      (targets in `heldout_spec.md`).
