# Prompt Protocol

> Prompts are **frozen before results are collected** (CLAUDE.md Rule #2) and
> **versioned**. RQ3 depends entirely on controlled, comparable prompts.
> Per Rule #9, prompt effects are reported as distinct from raw model capability.

## Principles

1. **Versioned registry:** every prompt lives in a committed registry with an id
   and a `prompt_registry_version`. Runs record which version they used.
2. **Model-agnostic *task* wording:** the described task (which object to locate)
   is identical across models; only model-required **wrapping** (chat template,
   system role, image-token placement) differs and is documented per model in
   [`model_matrix.md`](model_matrix.md).
3. **Two output regimes (see below).** We do **not** force a single foreign output
   format on every model — doing so would collapse Tier-A native grounding into
   Tier-C prompt-induced output. Instead, native models emit their *native* format
   and the evaluation adapter converts.
4. **No post-hoc tuning:** once results are collected, prompts do not change
   (CLAUDE.md Rule #2).

## Two prompt regimes (core design decision)

The benchmark is a **native-vs-prompted** study, so it uses two regimes. Note that
the two native models have **different documented primitives** (see
[`model_matrix.md`](model_matrix.md)):

- **Native regime (native conditions only).** Each native model is prompted in its
  **vendor-documented convention** and emits its **native primitive**:
  - **Qwen native bbox** — elicits `bbox_2d` (abs-px) → **BBox** metric family.
  - **Cosmos-native-point** — elicits `point_2d` (normalized 0–1000) → **Point**
    metric family. Cosmos is **not** asked for a native bbox (no documented bbox
    schema exists; asking would be prompt-induced, not native).
  The **adapter** converts to the family's canonical schema; the *prompt* never
  asks for a foreign format. These runs produce the RQ1 native-accuracy numbers.
- **Prompted regime (all five models — bounding box).** A single shared,
  plain-language prompt asks every model for a **bounding box** in one stated
  format. This includes **Cosmos-prompted-bbox**, which is **prompt-induced and
  never called native bbox**. For the three C-models this is the only available
  regime. These runs produce the RQ2 bbox contrast and the RQ4 Llama scale
  comparison. (Qwen also runs here, giving an all-five prompted-bbox surface.)

> **Fairness statement (must appear in the paper):** the native regime gives each
> native model its **documented primitive** (Qwen→box, Cosmos→point); the prompted
> regime is one identical bbox prompt for all five. Both are reported. A
> prompt-induced coordinate is never relabeled as native. **Point and bbox results
> are never presented as the same metric axis.**

## Complexity tiers (the RQ3 variable)

The same target object is described at increasing referring-expression complexity.
Tiers are the **independent variable** for RQ3 and a GT annotation field.

| Tier | Name | Definition | Example |
|------|------|-----------|---------|
| **L1** | Bare category | single noun / class label | "the dog" |
| **L2** | + attribute | category + 1 attribute (color/size) | "the brown dog" |
| **L3** | + spatial | attribute + spatial locator | "the brown dog on the left" |
| **L4** | Relational/compositional | multi-clause, relations to other objects | "the brown dog sitting next to the person holding a leash" |

> Tiers are **[Assumption]** — the exact rubric is finalized at freeze and applied
> consistently by annotators (see [`annotation_protocol.md`](annotation_protocol.md)).

## Prompt registry — source of truth

The committed registry **[`prompts/registry.json`](../prompts/registry.json)** is
the **source of truth** for all prompt text and the prompted output contract.
Anything below is a human-readable summary; on any discrepancy the registry wins.

> **Status:** `prompt_registry_version: 0.1.0-draft` — **NOT frozen.** Native
> prompt wording is still TBD-authoring; the prompted-bbox output contract is
> locked. Do not present draft-registry runs as frozen benchmark results.

**Prompted-bbox v1 output contract (LOCKED, Karar B)** — entry
`grounding.prompted.bbox.v1`, one shared template for all five models:
- The model must respond with a JSON object **`{"bbox": [x, y, w, h]}`**,
- coordinates in **absolute pixels**, layout **`xywh`** (`x,y` = top-left corner,
  `w,h` = width/height), origin top-left,
- or, if the object is absent, exactly **`NOT_PRESENT`**.

This layout **is** the canonical internal schema, so parsing → canonical is an
identity map (no `xyxy`↔`xywh` ambiguity, no point↔bbox coercion). Parse failures
are recorded separately, not silently scored (see [`metrics_spec.md`](metrics_spec.md)).

**Native regime (native conditions only):** the vendor-documented instruction for
each native condition — **Qwen** eliciting a **`bbox_2d`** box (xyxy abs-px),
**Cosmos-native-point** eliciting a **`point_2d`** point (normalized 0–1000).
Cosmos is **not** asked for a native box. Native wording is **TBD-authoring** in
the registry; the elicited output primitive is fixed.
- In the **native** regime, the model emits its native coordinate format and the
  **adapter** converts to canonical `xywh` abs-px — the prompt does not request a
  foreign format.
- The explicit `NOT_PRESENT` escape hatch (both regimes) enables honest
  hallucination and recall measurement — a model must be able to decline. This is
  exercised by the **negative probes** in the held-out set
  ([`heldout_spec.md`](heldout_spec.md)), since public REC data contains no
  absent-referent cases.

## Prompt-robustness set (RQ3 secondary axis)

Beyond the L1–L4 complexity tiers, RQ3 includes a **paraphrase-robustness**
probe: each target expression has ≥2 frozen paraphrases of equal complexity. The
set is frozen pre-run; the DV is within-model variance across paraphrases. This
measures sensitivity to surface wording independent of complexity.

## Registry schema

The committed registry is [`prompts/registry.json`](../prompts/registry.json)
(loaded via `experiments/prompt_registry.py`). Per-entry schema:

```json
{
  "prompt_id": "grounding.prompted.bbox.v1",
  "prompt_registry_version": "1.0.0",
  "regime": "native|prompted",
  "applies_to": ["all"] ,
  "tier": "L1|L2|L3|L4|paraphrase|template",
  "text_template": "...",
  "output_format_spec": "xywh_abs_pixels | native",
  "notes": "rationale / provenance"
}
```

- `regime: native` entries are Tier-A-only and set `output_format_spec: native`;
  `applies_to` names the specific model(s). `regime: prompted` entries apply to
  all five.

## Fairness & bias controls

- **Native regime** gives each Tier-A model its documented interface; **prompted
  regime** is one shared template for all five. Both regimes are reported.
- Model-specific chat wrapping is documented, not content-changed.
- Few-shot vs zero-shot is a **deliberate, documented choice** (default: zero-shot
  for v1) applied uniformly; if few-shot is used, exemplars are frozen and shared.
- Any model that cannot follow the output format is handled by the robust parser,
  and its **parse-failure rate is reported separately from localization** — a
  format failure is never counted as a localization failure without a flag (see
  [`metrics_spec.md`](metrics_spec.md)).
- A prompt-induced coordinate is **never** described as native grounding
  (CLAUDE.md Rule #9).

## Deliverables

- [ ] Frozen `prompts/registry.json` (or similar) committed + version tagged.
- [ ] Per-model wrapping notes in `model_matrix.md`.
- [ ] Tier rubric finalized and cross-referenced with annotation protocol.
