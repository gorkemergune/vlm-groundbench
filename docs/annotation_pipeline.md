# Annotation Pipeline

> **Status: Design (NOT frozen).** This document describes *how* grounding
> annotations are produced. It is **additive**: it **reuses** and **defers to** the
> existing LOCKED methodology and **changes none of it**. On any discrepancy, the
> LOCKED source documents win — see [Existing LOCKED contracts](#existing-locked-contracts).
>
> **No real annotation is produced by this document.** No images are selected, no
> boxes are drawn, no referring expressions are authored, no prompts are written,
> no models are run. **No TBD threshold/N/ratio/wording is filled in here.**

## Purpose / Scope

Define the operational pipeline for creating **human** bounding-box ground truth
paired with **natural-language referring expressions**, difficulty labels, and
negative probes, for the VLM-GroundBench grounding evaluation — **without**
redefining any existing contract.

In scope: annotation **schema mapping**, layer separation, bbox / referring-
expression / negative-probe / difficulty / multi-target protocols, quality
control, dataset manifest, and a pilot **plan**.

Out of scope (unchanged elsewhere, do not touch here): RQ1–RQ5, metric
definitions, the prompt registry contract, `families.py`, `matching.py`,
`benchmark_protocol.md` `protocol_version`, and the PRIMARY/SECONDARY dataset
decision.

## Raw vs GT vs Workflow vs Split layers

Preserves `dataset_spec.md` data layout and CLAUDE.md Rule #4 (raw preserved) /
Rule #5 (raw separated from derived).

| Layer | Location | Mutable? | Content |
|-------|----------|----------|---------|
| **Raw images** | `data/raw/` | **Never** (SHA-256 in manifest) | source images; never edited/resized/relabeled |
| **GT annotations** (immutable, versioned) | `data/annotations/` | Only via new version + CHANGELOG | the LOCKED GT schema from `dataset_spec.md` |
| **Workflow / QC state** (ADDITIVE, mutable, derived) | `data/annotations/_workflow/` | Yes | annotator assignment, status, adjudication, IAA overlap bookkeeping |
| **Splits** | `data/splits/` | Content-hashed manifest | per-sample → split mapping |

- **`data/annotations/_workflow/` is mutable workflow state and is NOT part of the
  immutable GT.** It exists so that process fields (annotator_id,
  annotation_status, adjudication_status) never mutate the LOCKED GT records.
- Any GT correction creates a **new version** with a `data/annotations/CHANGELOG.md`
  entry (who/when/why); the prior version is retained (Rule #1;
  `annotation_protocol.md` §Versioning).

## Existing LOCKED contracts

This pipeline **reuses, and does not modify**, the following (authoritative
sources in parentheses):

- **Canonical GT bbox format = `xywh_abs_pixels`, origin top-left** — LOCKED
  (`prompts/registry.json` `output_format_spec`; `dataset_spec.md` `box_format`;
  `metrics_spec.md` Conventions). This layout *is* the canonical internal schema;
  parsing→canonical is an identity map with **no xyxy↔xywh ambiguity and no
  point↔bbox coercion**.
- **GT schema** — the sample record in `dataset_spec.md` (Ground-truth schema).
- **No separate point GT** — GT is always a bounding box, for **all** models incl.
  Cosmos; a point prediction is scored point-in-GT-box, never IoU
  (`annotation_protocol.md` §Annotation unit; `heldout_spec.md` §0;
  `metrics_spec.md` Family B).
- **Complexity tiers L1–L4** — rubric in `prompt_protocol.md` (unchanged; no new
  tier categories).
- **`NOT_PRESENT` literal + negative-probe definition** — `prompts/registry.json`
  (`not_present_literal`); `heldout_spec.md` §4; `metrics_spec.md` (hallucination).
- **Difficulty axes** `{size_bin, occluded, clutter}`, size = **image-area-relative**
  (COCO absolute-pixel definition NOT used) — `heldout_spec.md` §5 (thresholds TBD).
- **IAA acceptance gates (LOCKED)** — `annotation_protocol.md` §Quality control.
- **Multi-target Hungarian matching** — canonical definition in `metrics_spec.md`;
  `evaluation/matching.py::hungarian_match` is intentionally **not implemented in
  Phase A** and is **not changed** by this document.
- **Immutability / versioning / no-model-pre-label** — `annotation_protocol.md`
  §Versioning, §Tooling; CLAUDE.md Rules #1, #6, #9.

## Annotation schema mapping

The **LOCKED GT record** (`dataset_spec.md`) is reused verbatim:
`sample_id, image_path, image_source_id, referring_expression,
prompt_complexity_tier, referent_present, gt_boxes[{x,y,w,h}],
box_format="xywh_abs_pixels", is_multi_target,
difficulty{size_bin, occluded, clutter}, categories, dataset_role,
contamination_suspect, license, provenance`.

Mapping of requested audit fields → contract:

| Requested field | Mapped to | Status |
|-----------------|-----------|--------|
| image_id | `sample_id` + `image_source_id` | existing |
| source / provenance | `provenance` + `license` + `contamination_suspect` + `dataset_role` | existing |
| split | `data/splits/` manifest (not a GT field) | existing (separate manifest) |
| GT bbox | `gt_boxes` **xywh** (never xyxy — see bbox protocol) | existing |
| target category | `categories` | existing |
| single/multi-target | `is_multi_target` | existing |
| size / occlusion / clutter | `difficulty{}` | existing (thresholds TBD) |
| referring expressions (≥2 paraphrase) | `referring_expression` + paraphrase grouping | **ADDITIVE** (see below) |
| negative probe | `referent_present=false` + `gt_boxes=[]` | existing; type tag ADDITIVE |
| target_id | — | **ADDITIVE / OPTIONAL** |
| ambiguity | — | **ADDITIVE / OPTIONAL** |
| annotator_id | workflow layer | **ADDITIVE (workflow, not GT)** |
| annotation_status | workflow layer | **ADDITIVE (workflow, not GT)** |
| adjudication_status | workflow layer | **ADDITIVE (workflow, not GT)** |

## ADDITIVE / OPTIONAL fields

The following are **ADDITIVE and OPTIONAL**. They **do not** modify the LOCKED GT
schema and are **not** made mandatory here. Whether any becomes required is a
future decision, not made in this document.

- **`target_id`** (ADDITIVE/OPTIONAL): stable id of a target within an image, so a
  referring expression can bind to a specific box in **multi-target** samples.
- **`paraphrase_group`** (ADDITIVE): groups the **≥2 frozen paraphrases** that
  refer to the **same** target at equal complexity (RQ3). The LOCKED schema stores
  one `referring_expression` per record; paraphrases are represented as sibling
  records sharing a `paraphrase_group` (+ `target_id`), **without** changing the
  single-expression GT contract or the `output_format_spec`.
- **`negative_type`** (ADDITIVE): `natural` | `constructed` (see negative-probe
  protocol).
- **`ambiguity`** (ADDITIVE/OPTIONAL): records an annotator/reviewer ambiguity flag
  and its resolution (rewrite vs mark multi-target).
- **Workflow fields** (ADDITIVE, `data/annotations/_workflow/` only, **never in the
  immutable GT**): `annotator_id`, `annotation_status`, `adjudication_status`.

## Bounding-box protocol

- **Canonical GT format = `xywh_abs_pixels`, origin top-left — LOCKED.** GT is
  **always** stored as `xywh` (`dataset_spec.md`, `prompts/registry.json`).
- **xyxy is permitted ONLY as the annotation tool's UI / internal representation.**
  It is **never** persisted to GT. If a tool emits `[x1,y1,x2,y2]`, it is converted
  deterministically to canonical `xywh` on export, and that conversion is
  **unit-tested** (aligns with the freeze checklist item "per-model coordinate
  conversions unit-tested"). Storing xyxy as GT would reintroduce the exact
  ambiguity the registry eliminated and is prohibited.
- **No point annotation task.** GT box serves both families; Cosmos-native-point is
  scored point-in-GT-box. **No point→bbox or bbox→point coercion.**
- **Human-authored GT only.** Models under evaluation never pre-label GT
  (`annotation_protocol.md` §Tooling; anti-circularity).
- **Box tightness:** smallest axis-aligned box fully containing the referent;
  occlusion convention (visible vs amodal) documented once and applied consistently
  (`annotation_protocol.md` §Guidelines 1–2).

## Referring-expression protocol

- **Tiers L1–L4** taken **verbatim** from `prompt_protocol.md` (no new categories):
  L1 bare category · L2 +attribute · L3 +spatial · L4 relational/compositional.
- **≥2 frozen paraphrases** per positive target, **equal complexity**, each
  resolving to the **same single** target (`heldout_spec.md` §3;
  `annotation_protocol.md` §7).
- **`output_format_spec` is fixed and unchanged across paraphrases** — only the
  `{referring_expression}` text varies; the format instruction
  (`xywh_abs_pixels` in the prompted regime, `native` in the native regime) stays
  constant (`prompts/registry.json`, entry `grounding.prompted.bbox.v1`).
- **Ambiguity rejection:** an expression matching >1 region is either rewritten to
  disambiguate or marked `is_multi_target=true` with **all** GT boxes — never
  silently reduced to one (`annotation_protocol.md` §Guidelines 3).

## Negative-probe protocol

- Contract preserved: `referent_present=false`, `gt_boxes=[]`, correct behavior =
  **`NOT_PRESENT`** (`prompts/registry.json`; `heldout_spec.md` §4).
- **`negative_type` (ADDITIVE):**
  - **natural** — the image contains **no** instance of the referent (e.g. "the
    person" in a person-free scene). Requires **human verification** of absence.
  - **constructed** — the image contains people but the **named object is absent**
    (e.g. "the dog" in a dog-free scene). Fully **human-authored**.
- Target must be **plausibly expected but genuinely absent** (not absurd /
  out-of-domain). Absurd/impossible referents are a **separate, optional sanity
  subset**, not the primary negatives (`heldout_spec.md` §4).
- **Negative fraction is TBD** (set after the power analysis; the 20–33 % range is
  non-binding planning only). **Not filled here.**

## Difficulty annotation

| Axis | Automatic? | Note |
|------|-----------|------|
| size **ratio** = GT box area / image area (image-area-relative) | **Automatic, after the box exists** | COCO absolute-pixel thresholds NOT used |
| `size_bin` (small/med/large) | **No** | small/med/large **thresholds TBD** — locked from the pilot distribution; **not filled here** |
| `occluded` (true/false) | **No — human/reviewer** | ≥X% occlusion threshold **TBD** |
| `clutter` (low/med/high) | **No — human/reviewer** | cutoffs **TBD** |

Only the size **ratio** is derived automatically once a box exists; mapping the
ratio to a `size_bin` waits on the TBD thresholds. **No threshold is chosen in this
document.**

## Multi-target / target_id

- The LOCKED schema already supports multi-target: `is_multi_target=true` with
  multiple `gt_boxes`.
- **`target_id` (ADDITIVE/OPTIONAL)** lets a referring expression bind to a specific
  box in a multi-target image (forward-compatibility for set-to-set scoring).
- **Matching is unchanged.** `metrics_spec.md` defines canonical Hungarian one-to-one
  matching; `evaluation/matching.py::hungarian_match` remains intentionally
  unimplemented in Phase A and is **not** touched. The schema (box list +
  `target_id`) is kept forward-compatible so Hungarian can be implemented later
  **without** re-annotation.
- HII (SECONDARY stress candidate) is multi-person by construction and is the
  natural source of future multi-target samples.

## Ambiguity handling

- Per `annotation_protocol.md` §Guidelines 3: if a referring expression resolves to
  more than one region, the annotator **either** rewrites it to a unique target
  **or** marks `is_multi_target=true` with all boxes — **never silently picks one**.
- The **ADDITIVE/OPTIONAL `ambiguity`** field records the flag and its resolution.
- HII carries **high** single-target ambiguity (many equivalent people); this makes
  it a stress source, not a clean single-target source.

## Quality control / IAA

Reuses the **LOCKED acceptance gates** (`annotation_protocol.md` §Quality control) —
**data-quality gates, not model-performance thresholds; not invented here:**

| Criterion | LOCKED gate |
|-----------|-------------|
| Box agreement (mean pairwise IoU, positive samples) | **≥ 0.70** |
| Tier-label agreement (κ) | **≥ 0.60** |
| Difficulty-label agreement (κ) | **≥ 0.60** |
| Negative-probe agreement on `referent_present` (κ) | **≥ 0.60** |

- **≥2 annotators**, overlap **≥ 20 %** of samples.
- **Adjudication** by a third reviewer; decisions logged in
  `data/annotations/CHANGELOG.md`.
- Also verified per sample: referring-expression validity (unique, self-contained),
  ambiguity rejection, and negative-probe validation (absence agreement).
- Samples below a gate are **fixed or dropped, never shipped noisy**.

## Manifest / provenance / dedup

- **Distinct from the run manifest.** `evaluation/manifest.py` (`RunManifest`)
  describes a model **run** and is **not** touched here.
- **Dataset/sample manifest (ADDITIVE)** per `dataset_spec.md` §Provenance: for each
  sample records `sample_id, image_source_id, SHA-256(raw), provenance="dataset@version",
  license, dataset_role, contamination_suspect, split, GT-version pointer`, and the
  three-layer dedup outcome (cryptographic hash + perceptual-hash + benchmark-corpus
  provenance check — `heldout_spec.md` §1b).
- **Dedup thresholds/method are TBD** (pHash method + distance threshold; exact/near
  thresholds) — recording format is fixed, values are **not filled here**.
- **Raw/derived separation:** `data/raw/` (immutable) ≠ `data/annotations/` (GT) ≠
  `data/annotations/_workflow/` (mutable state) ≠ `results/` (metrics).

## Pilot plan

**Plan only — no images selected, no annotation produced.**

- **Goal:** validate the schema, the tool export, and the IAA pipeline — **not**
  statistical power.
- **Scope:** a small **single-target** sample from **img2** and a small
  **multi-target** sample from **HII**. The specific files are **not** chosen here
  and **no** annotation is written.
- **Pilot N:** a small working figure, **non-binding / TBD** (final N comes from the
  per-tier power analysis; the ~200–500 held-out figure is non-binding). **Not fixed
  here.**
- **What the pilot must validate:** (a) tool export conforms to the LOCKED `xywh`
  GT schema; (b) L1–L4 + ≥2-paraphrase representation holds; (c) the IAA pipeline
  (IoU / κ) computes; (d) negative `natural`/`constructed` tagging records; (e) the
  automatic size-ratio computation is correct.

## Human vs automatic responsibilities

- **Human (required):** all GT box drawing; L1–L4 + paraphrase authoring;
  occlusion/clutter labels; ambiguity resolution/rejection; negative probes
  (natural absence verification + constructed authoring); img2 person/no-person
  census; IAA overlap + adjudication.
- **Automatic (allowed):** size **ratio** (after box), SHA-256 + perceptual-hash
  dedup bookkeeping, dataset-manifest generation. **No model/API is used to
  propose GT** (anti-circularity).

## PRIMARY / SECONDARY status

**Unchanged by this document (methodology lock preserved):**

- **PRIMARY = contamination-free-by-construction.**
- **img2 = `contamination_suspect` candidate** (not PRIMARY).
- **HII = SECONDARY stress candidate.**
- **Original Images = excluded** (PII + license + contamination; files not deleted).
- **PRIMARY = not yet exists.**

This pipeline is **source-agnostic**: the same schema/protocol applies to whichever
contamination-free source becomes PRIMARY and to the SECONDARY/stress sources.
Defining the pipeline does **not** promote any current source to PRIMARY.

## Blockers before real annotation

1. **PRIMARY source gap (critical):** no contamination-free image source exists yet;
   img2/HII/Original Images do not satisfy the lock. Requires a
   Research-Director-level decision + source acquisition.
2. **Pilot validation** of schema/tool/IAA.
3. **License + ethics/PII screening** for any source used (img2 provenance/license
   UNVERIFIED; img2 contains identifiable minors; HII has watermarked scraped
   personal photos; Original Images excluded).
4. **Tooling + ≥2 annotators + adjudicator** set up.

Real annotation does **not** start until these close.

## Explicit list of TBDs (preserved, not filled)

- `size_bin` small/medium/large thresholds.
- `occluded` occlusion-percentage threshold.
- `clutter` low/med/high cutoffs.
- Negative-probe fraction of the set.
- Held-out target N and pilot N (from the per-tier power analysis).
- Perceptual-hash method + distance threshold; exact/near-duplicate thresholds.
- Native prompt wording (Qwen `bbox_2d`, Cosmos `point_2d`) — TBD-authoring in the
  registry (elicited primitives already locked).

## Change-impact / immutability rules

- **No LOCKED file is modified** by adopting this document:
  `dataset_spec.md`, `heldout_spec.md`, `annotation_protocol.md`,
  `prompt_protocol.md`, `metrics_spec.md`, `benchmark_protocol.md`,
  `prompts/registry.json`, `evaluation/families.py`, `evaluation/matching.py`,
  `evaluation/metrics.py` — all unchanged.
- This document is **additive** and **subordinate**: on any conflict, the LOCKED
  sources govern.
- ADDITIVE fields are **optional**; none is made mandatory here.
- GT is **immutable + versioned**; corrections go through a new version +
  `CHANGELOG.md` (Rule #1). Raw images are never edited (Rule #4) and are separated
  from derived data (Rule #5). No TBD value is decided in this document.
