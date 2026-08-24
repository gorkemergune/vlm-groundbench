# Held-Out Custom Set — Specification

> **Status:** Design (no data collected). This set is the **PRIMARY evidence** for
> the main grounding claim (RQ1/RQ2) and the **only** source of hallucination
> negative probes and difficulty labels. Built and IAA-verified per
> [`annotation_protocol.md`](annotation_protocol.md); schema in
> [`dataset_spec.md`](dataset_spec.md); metrics in [`metrics_spec.md`](metrics_spec.md).

## Why this set exists

RefCOCO/+/g and Visual Genome are standard grounding-pretraining corpora for the
Tier-A models (Qwen2.5-VL, Cosmos3-Nano-Reasoner), so public scores may reflect
memorization, not localization. This set is constructed to be **contamination-free**
so it can carry the headline RQ1/RQ2 claim, with public benchmarks reported
alongside as contamination-suspect.

## 0. Ground-truth representation (applies throughout)

**GT is always a bounding box.** This set annotates object/referent **boxes**
only — there is **no separate point GT**, including for Cosmos.
**Cosmos-native-point** predictions are scored against the GT **box** (point-in-GT-
box accuracy; see [`metrics_spec.md`](metrics_spec.md)). There is **no point→bbox
or bbox→point coercion** in either direction, and a point is never scored with IoU.

## 1. Image eligibility (what makes an image admissible)

An image is eligible **only if all** of the following hold:

1. **Not from a known grounding corpus.** Not present in COCO / RefCOCO(+/g) /
   Visual Genome / Flickr30k / other common REC-VQA training sets. Enforced by the
   three-layer dedup/contamination procedure below.
2. **Licensing permits our use + redistribution of a small sample.** Source
   license recorded per image; we assign the set's license. Prefer sources we can
   redistribute (own captures or permissively licensed). **Do not invent** a
   license — mark TBD until confirmed.
3. **Freshly annotated by us.** Referring expressions are authored for this set
   and have never been published (so they cannot be in any pretraining corpus).
4. **Natural photographic content** with at least one unambiguously describable
   target (or, for negative probes, a plausibly-expected-but-absent object).
5. **No PII / sensitive content**; standard ethics screening.

### 1b. Dedup & contamination procedure (three layers)

1. **Exact duplicate** → **cryptographic hash** of the image bytes (e.g. SHA-256).
2. **Near duplicate** → **perceptual-hash-based** check against the held-out set
   and the known corpora.
3. **Benchmark contamination** → **provenance check** against known
   benchmark/source corpora (COCO / RefCOCO(+/g) / Visual Genome / Flickr30k / …).

**Still TBD (do not invent):** the specific perceptual-hash method, the pHash
distance threshold, and the exact/near-duplicate operational thresholds — these are
confirmed on a pilot before freeze. All dedup/contamination results are recorded in
the **provenance / split manifest** in a **reproducible** way (checksums per
`dataset_spec.md`).

Provenance, capture/source date, and the dedup result are logged per image in the
manifest (checksums per `dataset_spec.md`).

## 2. Composition & balance

The set is stratified so each analysis axis has support (exact counts **TBD** from
the per-tier power analysis; working target ~200–500 images, not fixed):

- **Prompt-complexity tiers** L1–L4 (same rubric as
  [`prompt_protocol.md`](prompt_protocol.md)), balanced.
- **Positive vs negative** referents (negative probes, §4).
- **Difficulty strata** (§5): size bins, occlusion, clutter.
- **Single- vs multi-target** referents (multi-target flagged).
- Category diversity beyond COCO-80 where possible (to test open-vocabulary).

## 3. Referring-expression authoring

- Expressions are natural, grammatical, self-contained (no reliance on external
  context), and authored to resolve to a **single** target unless explicitly a
  multi-target sample.
- Each target carries **≥2 frozen paraphrases** of equal complexity for the RQ3
  paraphrase-robustness probe.
- Expressions are frozen before any model is run (CLAUDE.md Rule #2).

## 4. Negative probes (hallucination evaluation)

Negative probes are the mechanism that makes hallucination measurable (public REC
data has no absent-referent cases). A negative probe is a sample where:

- The referring expression names an object that is **plausibly expected but
  genuinely absent** from the image (e.g., "the umbrella" in a clearly
  umbrella-free beach scene) — not an absurd/out-of-domain object.
- **`referent_present = false`**, `gt_boxes = []`.
- **Correct model behavior = `NOT_PRESENT`.** Returning any box = an
  absent-object hallucination (`hall_absent`, see `metrics_spec.md`).

Design rules:
- Negative probes are **matched** to positive samples where feasible (same scene
  type / expression style) so hallucination is not confounded by scene oddity.
- A documented fraction of the set is negative. **The fraction is still TBD** and
  is **not** fixed here: it is set **after the power analysis** by jointly
  weighing the `hall_absent` CI requirement (E4) and the positive N needed for the
  primary endpoints (RQ1/RQ2). **20–33 % is only a non-binding planning range**,
  not a decision (see `experiment_plan.md`).
- Absurd/impossible referents are a separate, optional sanity subset — **not**
  the primary negative probes (too easy; not representative).

## 5. Difficulty labels (annotation-time, per sample)

Each sample is labeled on three axes (also in the GT schema `difficulty` field):

| Axis | Values | Definition |
|------|--------|-----------|
| `size_bin` | small / medium / large | **GT box area / image area** (image-area-relative). The COCO absolute-pixel `<32²` / `>96²` definition is **NOT used**. The small/medium/large **percentage thresholds are still TBD** (locked from the pilot/dataset distribution before freeze). |
| `occluded` | true / false | target substantially occluded by another object/edge (documented ≥ X% threshold, **TBD**) |
| `clutter` | low / med / high | number of same-category distractors / overall scene density (**cutoffs TBD**) |

- For **small** targets, report **center-distance** alongside IoU (IoU is unstable
  at small scale) — see E3 in [`experiment_plan.md`](experiment_plan.md).
- Difficulty labels are assigned by annotators and included in the IAA overlap.

## 6. Duplicate objects & matching (annotation side)

- If an expression matches **>1** region, the annotator either (a) rewrites it to
  disambiguate, or (b) marks the sample `is_multi_target=true` with all GT boxes —
  never silently picks one (per `annotation_protocol.md`).
- **Duplicate/identical GT objects** (genuinely repeated referents) are captured
  as multi-target; scoring uses set-to-set Hungarian matching
  (`metrics_spec.md`). How **multiple predicted** boxes are scored (headline =
  first box; secondary = best-IoU; dedup at IoU ≥ 0.95) is defined in
  `metrics_spec.md` and applies uniformly here.

## 7. Annotation requirements & quality

Per [`annotation_protocol.md`](annotation_protocol.md):

- **Box tightness:** smallest axis-aligned box fully containing the referent.
- **Occlusion convention:** annotate a documented, consistent extent (visible vs
  amodal — record the choice).
- **≥2 annotators** on an overlap subset (≥20%); report box IAA (mean pairwise
  IoU) and tier/difficulty/negative-probe κ. **Acceptance thresholds are LOCKED**
  in [`annotation_protocol.md`](annotation_protocol.md): box mean IoU ≥ 0.70;
  tier κ ≥ 0.60; difficulty κ ≥ 0.60; negative-probe κ ≥ 0.60 (data-quality gates,
  not model-performance thresholds).
- Adjudication by a third reviewer; decisions logged.
- Annotations are **immutable + versioned**; corrections create a new version with
  a changelog (Rule #1). **No model under evaluation** is used to pre-label GT
  (avoids circularity).

## 8. Freeze checklist (held-out set)

- [ ] Eligibility + dedup procedure finalized and run; provenance logged.
- [ ] Target N met (from per-tier power analysis).
- [ ] Tier / positive-negative / difficulty balance achieved and recorded.
- [ ] Paraphrases authored and frozen.
- [ ] IAA computed and above thresholds; adjudication complete.
- [ ] License per image confirmed (no invented licenses; TBD resolved).
- [ ] Manifest with checksums committed; expressions frozen (Rule #2).
