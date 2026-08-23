# Benchmark Protocol

> **This is the freeze document.** Per CLAUDE.md "Research Integrity", the
> protocol must be frozen before final evaluation. After freeze, changes require
> a version bump and re-run — not silent edits.
>
> **Status: NOT frozen.** Aligned with the finalized native-vs-prompted
> methodology; remaining `[⚠ verify]`/TBD items must close before freeze.

## Protocol version

`protocol_version: 0.1.0-draft` → bump to `1.0.0` at freeze (not yet).

## Study framing (governs the whole protocol)

This is a **native-vs-prompted localization study**. Models are classified by *how*
they produce coordinates **and by which spatial primitive is natively documented**
(see [`model_matrix.md`](model_matrix.md)):

- **A-bbox — native bounding box:** Qwen2.5-VL-7B (`bbox_2d`) → **BBox** metric
  family.
- **A-point — native point:** Cosmos3-Nano-Reasoner (`point_2d`, 0–1000) →
  **Point** metric family. **Cosmos has no documented native bbox schema; it is
  never called native bbox.**
- **C — prompt-induced coordinates:** Llama 3.2 11B/90B Vision, Nemotron 3 Nano
  Omni (retain Tier-B *localization ability*; coordinates only via prompting).

**Labeling rule:** every prediction carries its **primitive** (bbox|point) and
**condition** label. A **prompt-induced coordinate is never described as native**,
and **A-bbox and A-point are never scored with the same metric or merged into one
ranking** (CLAUDE.md Rule #9; see [`metrics_spec.md`](metrics_spec.md)).

**Primary vs secondary evidence:** the **contamination-free custom held-out set**
([`heldout_spec.md`](heldout_spec.md)) is the **PRIMARY** evidence for the main
grounding claim (RQ1/RQ2). Public datasets (RefCOCO/+/g, Visual Genome, Flickr30k
Entities) are **SECONDARY** and **labeled contamination-suspect** wherever
reported (they are standard grounding-pretraining corpora for Tier-A models).

## Terminology: two distinct meanings of "tier"

The word **tier** is used in two unrelated senses in this benchmark. Always
qualify it as **"capability tier"** or **"complexity tier"** whenever ambiguity is
possible.

- **Capability tier** (how a model produces coordinates, and which primitive):
  - **A** = native/documented localization, subdivided by primitive:
    - **A-bbox** = native bounding box (Qwen).
    - **A-point** = native point (Cosmos; no documented native bbox).
  - **B** = visual localization/reasoning **without** a documented coordinate
    output.
  - **C** = prompt-induced coordinate localization (coordinates exist only because
    the prompt asked; not a documented capability).
- **Prompt-complexity tier** (how hard the referring expression is):
  - **L1–L4** (bare category → attribute → spatial → relational/compositional;
    rubric in [`prompt_protocol.md`](prompt_protocol.md)).

## Pipeline (model-agnostic)

```
frozen inputs                 per-model adapter            deterministic eval
┌────────────────┐   image    ┌──────────────────┐  raw   ┌────────────────────────┐
│ image + prompt │──+prompt──▶│ VLM inference    │──────▶│ parse → convert coords │
│ (frozen,       │  (regime:   │ (via adapter,   │ output │ → match → metrics      │
│  tier-labeled) │  native|    │  thin)          │        │ (tier-labeled)         │
└────────────────┘  prompted)  └──────────────────┘        └────────────────────────┘
        │                             │                            │
   data/splits              results/raw_outputs           results/metrics
```

- **Inputs are frozen:** the (image, prompt, GT) triples come from a committed,
  hashed split manifest. Same inputs for every model (fairness).
- **Two prompt regimes** (see next section): native (Tier A) and shared prompted
  (all five).
- **Adapters are thin:** an adapter only (a) sends the frozen prompt+image to a
  model and (b) returns the raw response verbatim. It performs **no scoring** and
  **no coordinate conversion** — conversion lives in the eval layer.
- **Raw ≠ derived:** raw model outputs are saved untouched (Rule #4) and stored
  separately from metrics (Rule #5). Metrics are recomputable from raw (Rule #7).

## Two prompt regimes

- **Native regime (Tier-A only):** each native model is prompted in its
  vendor-documented grounding convention and emits its **native** coordinate
  format (Qwen `bbox_2d` abs-px; Cosmos box/`point_2d` normalized 0–1000). The
  eval layer converts to canonical `xywh` abs-px. The prompt never requests a
  foreign format (that would collapse Tier A into Tier C). Produces the RQ1
  native-accuracy numbers.
- **Prompted regime (all five):** one shared, plain-language prompt asks every
  model for a box in one stated format. For Tier-C models this is the only
  available regime; any box is labeled **prompt-induced**. Produces the RQ2
  A-vs-C contrast and the RQ4 Llama scale comparison.

Full wording and the versioned registry live in
[`prompt_protocol.md`](prompt_protocol.md).

## What is held constant

| Factor | Setting | Rationale |
|--------|---------|-----------|
| Image set | frozen split (held-out primary + public secondary) | fair comparison |
| Prompt registry | frozen + versioned (`prompt_protocol.md`) | Rule #2, RQ3 control |
| Prompt regime | fixed per experiment (native for E1a; prompted for E1b) | native-vs-prompted design |
| Coordinate convention | canonical `xywh` abs px (`dataset_spec.md`) | avoid IoU bugs |
| Decoding params | fixed per run, logged | reproducibility |
| Image preprocessing | fixed, scripted | reproducibility |
| Random seeds | fixed + recorded | reproducibility |

Within an experiment, only the **declared variable** changes (model, prompt tier,
or difficulty stratum); the **regime** is fixed per experiment; everything else is
held constant.

## Experiment catalog (see `experiment_plan.md` for full detail)

| ID | Name | Regime | Conditions | Answers | Primary metric (family) |
|----|------|--------|-----------|---------|-------------------------|
| **E1a** | Native-regime localization | native | Qwen-native-bbox; **Cosmos-native-point** | RQ1, RQ2 (native arm), RQ5 | **Acc@IoU** (bbox); **point-in-GT-box acc** (point) |
| **E1b** | Prompted bbox localization, all five | prompted | all five incl. **Cosmos-prompted-bbox** | RQ2 (bbox contrast + within-Cosmos), RQ4 (Llama pair), RQ5 | **Acc@IoU** (bbox) |
| **E2** | Prompt robustness / paraphrase sensitivity | both, per model | all five | RQ3 | IoU/F1 per complexity tier; within-model Δ |
| **E3** | Difficulty-stratified localization | as E1a/E1b | native (acc) + all five (behavior) | RQ1 depth | Acc@IoU / point-in-GT-box acc per stratum |
| **E4** | Hallucination / negative probes | prompted (+ native) | all five | RQ1/RQ2 secondary | `hall_absent`, `hall_wrongbox`/`hall_wrongpoint` |

> **Cosmos conditions map onto existing IDs** — Cosmos-native-point ⊂ E1a,
> Cosmos-prompted-bbox ⊂ E1b. **No new top-level experiment ID is created.**

**RQ5 frontiers:** latency/cost is reported on **two separate Pareto frontiers** —
**local** {Qwen, Llama 11B, Llama 90B} and **NIM-API** {Cosmos, Nemotron}. Cross-
frontier latency is not a model property and is never merged.

## Per-condition coordinate conversion (eval layer)

Each condition is converted to **its family's** canonical schema (BBox → `xywh`
abs-px; Point → `(x,y)` abs-px), per the rules in
[`model_matrix.md`](model_matrix.md). **A point is never converted to a box or
scored with IoU.**

- **Qwen-native-bbox:** `bbox_2d [x1,y1,x2,y2]` abs-px → `w=x2−x1, h=y2−y1` (BBox).
- **Cosmos-native-point:** `point_2d [x,y]` normalized 0–1000 → multiply by
  `(W/1000, H/1000)` using **post-preprocessing** image `W,H` → `(x,y)` abs-px
  (**Point**).
- **Cosmos-prompted-bbox:** box elicited by prompt (no native bbox schema) → robust
  parse; **labeled prompt-induced** (BBox).
- **Llama 11B/90B, Nemotron, Qwen-prompted:** robust parse of prompt-induced box;
  parse failures flagged; labeled prompt-induced (BBox).

Conversions are **unit-tested against known boxes/points** before any reported run
(top source of silent IoU/point-error bugs).

## Output parsing, parse-success & fairness

- **Robust parser applied uniformly** so a model is not penalized for cosmetic
  formatting; per-model parsing rules are documented in
  [`model_matrix.md`](model_matrix.md) and frozen with the protocol.
- **Parse-success rate is a first-class, separately-reported metric** — never
  folded into IoU/Acc@IoU. This separates "cannot format a box" from "cannot
  localize" (essential to the RQ2 native-vs-prompted claim). Definition and the
  dual Acc@IoU basis (parse-failure charged vs excluded) are in
  [`metrics_spec.md`](metrics_spec.md).
- **Non-answers / refusals / `NOT_PRESENT`** are recorded explicitly and feed the
  hallucination and recall accounting.

## Metrics summary (full definitions in `metrics_spec.md`)

**Two spatial metric families — never merged, point never scored with IoU:**
- **Family A — BBox:** **primary = Acc@IoU** at **τ = 0.5 and τ = 0.75**, plus
  mean/median IoU. Applies to Qwen native bbox and all prompt-induced boxes
  (incl. Cosmos-prompted-bbox).
- **Family B — Point:** **primary = point-in-GT-box accuracy**, plus normalized
  point error / center-distance. Applies to Cosmos-native-point only.

- **First-class:** parse-success rate (per family, per condition).
- **Secondary:** Precision/Recall/F1 (multi-target/detection), hallucination
  (`hall_absent`; `hall_wrongbox` for boxes / `hall_wrongpoint` for points),
  latency, tokens/cost.
- **mAP:** **secondary, detection-subset only** (VG/Flickr) and only where a model
  emits usable ranking scores; otherwise **N/A**. **Not a primary metric for any
  RQ.**
- **Matching (bbox):** single-target headline = model's **first** box (secondary =
  best-IoU); **multi-target = Hungarian one-to-one** with `IoU ≥ τ`, unmatched
  pred→FP, unmatched GT→FN; **duplicate predictions** deduplicated at `IoU ≥ 0.95`
  before matching.
- **Negative probes:** samples with `referent_present = false` (no GT box);
  correct behavior is `NOT_PRESENT`; a returned box **or point** is an
  absent-object hallucination. Negative probes come from the held-out set (public
  REC data has no absent-referent cases).

## Run manifest (captured for every run)

Every run writes a manifest under `results/raw_outputs/<run_id>/manifest.json`:

```json
{
  "run_id": "E1a_qwen25vl7b_native_2026-08-22T...Z",
  "protocol_version": "0.1.0-draft",
  "experiment_id": "E1a",                      // E1a|E1b|E2|E3|E4
  "model_id": "...",
  "capability_class": "A-bbox",                // A-bbox | A-point | C
  "condition": "Qwen-native-bbox",             // Qwen-native-bbox | Cosmos-native-point | Cosmos-prompted-bbox | <model>-prompted-bbox
  "metric_family": "bbox",                     // bbox | point
  "prompt_regime": "native",                   // native | prompted
  "dataset_role": "heldout",                   // heldout (primary) | public_secondary
  "contamination_suspect": false,              // true for public_secondary
  "model_version_or_revision": "...",          // [⚠ verify per provider; capture returned model version for NIM APIs]
  "prompt_registry_version": "...",
  "split_manifest_hash": "sha256:...",
  "decoding_params": {"temperature": 0, "...": "..."},
  "seed": 0,
  "env_hash": "sha256 of pinned env",
  "timestamp_utc": "...",
  "code_git_commit": "..."
}
```

## Determinism & reproducibility rules

1. Fixed seeds; greedy/temperature-0 decoding where the model supports it
   (**[⚠ verify per model]** — NIM/hosted APIs may not be deterministic even at
   T=0; capture the returned model version per call to detect drift).
2. Pinned environment (see [`../models/`](../models) and repo env files).
3. **Deterministic metric recomputation:** all headline metrics are recomputable
   by re-running the single deterministic evaluator over saved raw outputs; a
   re-run must reproduce identical numbers (Rule #7). The evaluator never writes
   to raw outputs and never edits GT.
4. **Raw-output preservation:** raw model responses are saved verbatim and
   untouched (Rule #4), stored separately from derived metrics (Rule #5); no
   manual edits to raw outputs or metrics (Rules #4, #6).

## Freeze checklist (must all be ✅ before final eval — NOT yet complete)

- [ ] RQs/hypotheses frozen (`research_questions.md`)
- [ ] Dataset roles + licenses + splits frozen (`dataset_spec.md`); public
      versions pinned (RefCOCOg = UMD split), manifests hashed
- [ ] **Held-out set built + IAA-verified** (`heldout_spec.md`,
      `annotation_protocol.md`); negative probes + difficulty labels complete
- [ ] Prompt registry frozen + versioned, **both regimes** (`prompt_protocol.md`)
- [ ] Metric definitions frozen — Acc@IoU primary, mAP detection-subset only
      (`metrics_spec.md`)
- [ ] Model matrix `[⚠ verify]`/TBD closed: API determinism, pricing, Cosmos
      bbox key, Llama API coverage, Cosmos NIM license (`model_matrix.md`)
- [ ] Per-model coordinate conversions **unit-tested** against known boxes
- [ ] Environment pinned; run manifest schema implemented
- [ ] **Per-tier** power analysis done; held-out target N met

At freeze: bump `protocol_version` to `1.0.0` and tag the git commit. **(Do not
freeze until every box above is checked.)**
