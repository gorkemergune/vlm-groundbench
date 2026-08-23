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

The benchmark is a **native-vs-prompted** study, so it uses two regimes:

- **Native regime (Tier-A only — Qwen2.5-VL, Cosmos3-Nano-Reasoner).** Each native
  model is prompted in its **vendor-documented grounding convention** and emits its
  **native** coordinate format (Qwen `bbox_2d` abs-px; Cosmos box/`point_2d`
  normalized 0–1000). The **adapter** converts to the canonical `xywh` abs-px
  schema; the *prompt* never asks for a foreign format. These runs produce the
  RQ1 native-accuracy numbers.
- **Prompted regime (all five models).** A single shared, plain-language prompt
  asks every model for a bounding box in one stated format. For Tier-C models this
  is the *only* regime available, and any resulting box is labeled
  **prompt-induced** (never "native grounding"). These runs produce the RQ2
  A-vs-C contrast and the RQ4 Llama scale comparison.

> **Fairness statement (must appear in the paper):** the native regime gives
> Tier-A models their documented interface; the prompted regime is identical for
> all five. Both are reported. Neither regime is used to relabel a prompt-induced
> coordinate as native grounding.

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

## Prompt templates (illustrative — not yet frozen)

**Prompted regime (all five models):**
```
  "Locate the object described below in the image and return its bounding box.
   Description: {referring_expression}
   Respond with the bounding box as {OUTPUT_FORMAT_SPEC}.
   If the object is not present, respond exactly: NOT_PRESENT."
```

**Native regime (Tier-A only):** the vendor-documented grounding instruction for
each of Qwen2.5-VL and Cosmos3-Nano-Reasoner, eliciting the model's native output
(`bbox_2d` / `point_2d`-style JSON). The exact per-model wording is recorded in
the registry and cross-referenced in [`model_matrix.md`](model_matrix.md).

- In the **prompted** regime, `{OUTPUT_FORMAT_SPEC}` is a single shared spec for
  all models; parse failures are recorded, not silently scored (see
  [`metrics_spec.md`](metrics_spec.md)).
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

## Registry schema (proposed)

```json
{
  "prompt_id": "grounding.prompted.v1",
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
