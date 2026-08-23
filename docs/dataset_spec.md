# Dataset Specification

> **Status:** Draft. No data has been downloaded (per task constraints).
> Candidate sources below are **[⚠ Needs verification]** for current license
> terms and availability before any acquisition.

## Purpose

Define exactly which images and ground-truth grounding annotations the benchmark
uses, their provenance, licensing, splits, and preprocessing — so the evaluation
set is fixed and reproducible.

## Requirements the dataset must satisfy

1. **Bounding-box ground truth** paired with **natural-language referring
   expressions** (not just bare category labels), to support RQ3.
2. **Permissive, clearly documented license** compatible with public release of
   derived metrics (and, ideally, redistribution of a small sample).
3. **Diversity** across object categories, scene types, and expression complexity.
4. **Sufficient size for statistical power** — target set by a pre-registration
   power analysis (see [`experiment_plan.md`](experiment_plan.md)); a small,
   fully hand-verified set is acceptable for v1.

## Dataset roles (decided)

The benchmark uses a **contamination-free custom held-out set as PRIMARY evidence**
for the main grounding claim (RQ1/RQ2), with public benchmarks as **SECONDARY**
and **explicitly labeled contamination-suspect** wherever reported. Rationale:
RefCOCO/+/g and Visual Genome are standard grounding-pretraining corpora for the
Tier-A models, so public scores may reflect memorization (see
[`research_questions.md`](research_questions.md), contamination threat).

| Source | Role | Task fit | License (verified) | Contamination |
|--------|------|----------|--------------------|---------------|
| **Custom held-out set (ours)** | **PRIMARY** | Basic/attribute/relational/multi-object + negative probes + difficulty labels | We assign; freshly annotated | **Contamination-free by construction** (see `heldout_spec.md`) |
| RefCOCO | Secondary | Basic single-object REC | Annotations on COCO images (COCO terms) **[⚠ verify current]** | **Suspect** |
| RefCOCO+ | Secondary | Attribute (no location words) | as RefCOCO **[⚠ verify]** | **Suspect** |
| RefCOCOg (UMD split) | Secondary | Relational / long expressions | as RefCOCO **[⚠ verify]** | **Suspect** |
| Visual Genome | Secondary / detection subset | Relations + attributes | **CC BY 4.0** [Verified] | **Suspect** |
| Flickr30k Entities | Secondary (multi-object) | Phrase grounding | **Non-commercial research/education; images = Flickr ToU** [Verified] → **reference-only, do not redistribute images** | High |

> **Do not commit source images** (COCO/Flickr) to the repo; ship image IDs +
> download scripts + derived annotations. Visual Genome (CC BY 4.0) is the only
> public source whose annotations may be redistributed with attribution.
> **Do not invent** sizes, contamination rates, or licenses; unknowns are TBD.

## Data layout (repo convention)

```
data/
├── raw/          # untouched source images (never edited)      [gitignored if large]
├── processed/    # resized/normalized images for inference
├── annotations/  # ground-truth boxes + referring expressions  (immutable — Rule #1)
└── splits/       # frozen split manifests (json/csv of ids)
```

- **Rule #1 (CLAUDE.md):** ground-truth annotations are never modified
  automatically. Corrections go through the annotation protocol with human review
  and are versioned.
- Large binaries are excluded from git; a **manifest with checksums** is committed
  so the exact set is reconstructable.

## Ground-truth schema (proposed)

```json
{
  "sample_id": "string (stable, unique)",
  "image_path": "data/processed/....",
  "image_source_id": "original dataset id",
  "referring_expression": "the pig on the left",
  "prompt_complexity_tier": "L1|L2|L3|L4",
  "referent_present": true,
  "gt_boxes": [{"x": 0, "y": 0, "w": 0, "h": 0}],
  "box_format": "xywh_abs_pixels",
  "is_multi_target": false,
  "difficulty": {"size_bin": "small|medium|large", "occluded": false, "clutter": "low|med|high"},
  "categories": ["pig"],
  "dataset_role": "heldout|public_secondary",
  "contamination_suspect": false,
  "license": "source license id",
  "provenance": "dataset@version"
}
```

- **`referent_present: false`** marks a **negative probe** (no GT box; correct
  model behavior is `NOT_PRESENT`) — see hallucination metric in
  [`metrics_spec.md`](metrics_spec.md) and [`heldout_spec.md`](heldout_spec.md).
- **`contamination_suspect`** is `true` for all public-benchmark samples and is
  carried into every reported table.
- **Coordinate convention** is fixed here (`xywh`, absolute pixels, origin
  top-left) and every model adapter must map to it (Qwen `xyxy` abs-px; Cosmos
  normalized 0–1000 → convert). Ambiguity in coordinate conventions is a top
  source of silent IoU bugs; conversions are unit-tested (see `model_matrix.md`).

## Splits policy

- Benchmark is **evaluation-only** → primary split is a frozen **test** set.
- Optional small **dev** set for prompt/parsing debugging only; never used for
  reported headline numbers.
- Split manifests are content-hashed and committed under `data/splits/`.

## Provenance & integrity

- Record dataset name, version, URL, download date, and SHA-256 per file in a
  committed `data/MANIFEST.*`.
- Any preprocessing (resize, format) is scripted and logged; raw is preserved.

## Held-out set (primary) — specification pointer

The eligibility criteria, negative-probe definition, difficulty labels, and
annotation requirements for the primary held-out set are specified in
[`heldout_spec.md`](heldout_spec.md). It is built and IAA-verified per
[`annotation_protocol.md`](annotation_protocol.md) before freeze.

## Open questions to resolve before freeze

- [ ] Held-out target N from **per-tier** power analysis (working figure
      ~200–500 images, **TBD** pending analysis — not fixed).
- [ ] RefCOCO/COCO current license terms confirmed for redistribution of derived
      files (**[⚠ verify]**).
- [ ] Public-source versions pinned (RefCOCOg = UMD split) + manifests hashed.
- [ ] Whether a redistributable sample can be committed (VG CC BY 4.0 yes; COCO/
      Flickr images no — IDs+scripts only).
