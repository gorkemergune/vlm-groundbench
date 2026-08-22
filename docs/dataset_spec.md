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

## Candidate sources — [⚠ Needs verification]

The following are commonly used referring-expression / grounding datasets. Each
must be checked for **current** license and terms before use; do not assume.

| Candidate | Task fit | License note | To verify |
|-----------|----------|--------------|-----------|
| RefCOCO / RefCOCO+ / RefCOCOg | Referring expressions + boxes | Built on COCO images | Current license terms & attribution |
| Visual Genome (region descriptions) | Region-level descriptions | — | License, box quality |
| Flickr30k Entities | Phrase grounding | — | Redistribution terms |
| Hand-curated micro-set (ours) | Full control, small | We assign license | Annotation cost (see annotation protocol) |

> We adopt **one** primary source for v1 + optionally a small hand-annotated
> control set. Decision is recorded here once made, with citation.

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
  "gt_boxes": [{"x": 0, "y": 0, "w": 0, "h": 0}],
  "box_format": "xywh_abs_pixels",
  "categories": ["pig"],
  "license": "source license id",
  "provenance": "dataset@version"
}
```

- **Coordinate convention** is fixed here (`xywh`, absolute pixels, origin
  top-left) and every model adapter must map to it. Ambiguity in coordinate
  conventions is a top source of silent IoU bugs.

## Splits policy

- Benchmark is **evaluation-only** → primary split is a frozen **test** set.
- Optional small **dev** set for prompt/parsing debugging only; never used for
  reported headline numbers.
- Split manifests are content-hashed and committed under `data/splits/`.

## Provenance & integrity

- Record dataset name, version, URL, download date, and SHA-256 per file in a
  committed `data/MANIFEST.*`.
- Any preprocessing (resize, format) is scripted and logged; raw is preserved.

## Open questions to resolve before freeze

- [ ] Final primary dataset chosen + license confirmed (**[⚠ Needs verification]**).
- [ ] Target N from power analysis.
- [ ] Whether a redistributable sample can be committed to the repo.
