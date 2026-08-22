# Prompt Protocol

> Prompts are **frozen before results are collected** (CLAUDE.md Rule #2) and
> **versioned**. RQ3 depends entirely on controlled, comparable prompts.
> Per Rule #9, prompt effects are reported as distinct from raw model capability.

## Principles

1. **Versioned registry:** every prompt lives in a committed registry with an id
   and a `prompt_registry_version`. Runs record which version they used.
2. **Model-agnostic wording:** the *instruction* content is identical across
   models; only model-required **wrapping** (chat template, system role, image
   token placement) differs and is documented per model in
   [`model_matrix.md`](model_matrix.md).
3. **Output-format instruction is fixed** and identical across models so parsing
   is fair (see benchmark protocol parsing-fairness note).
4. **No post-hoc tuning:** once results are collected, prompts do not change.

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

## Prompt template (baseline, illustrative — not yet frozen)

```
Instruction (fixed across models):
  "Locate the object described below in the image and return its bounding box.
   Description: {referring_expression}
   Respond with the bounding box as {FIXED_OUTPUT_FORMAT}.
   If the object is not present, respond exactly: NOT_PRESENT."
```

- `{FIXED_OUTPUT_FORMAT}` is a single, fixed specification for all models.
  The canonical target is `xywh` absolute pixels (`dataset_spec.md`); if a model
  natively emits normalized coords, the **adapter** converts — the *prompt* does
  not change per model.
- The explicit `NOT_PRESENT` escape hatch enables honest hallucination and
  recall measurement (a model should be able to decline).

## Registry schema (proposed)

```json
{
  "prompt_id": "grounding.baseline.v1",
  "prompt_registry_version": "1.0.0",
  "tier": "L1|L2|L3|L4|template",
  "text_template": "...",
  "output_format_spec": "xywh_abs_pixels",
  "notes": "rationale / provenance"
}
```

## Fairness & bias controls

- One shared baseline template; model-specific chat wrapping documented, not
  content-changed.
- Few-shot vs zero-shot is a **deliberate, documented choice** (default: zero-shot
  for v1) applied uniformly; if few-shot is used, exemplars are frozen and shared.
- Any model that cannot follow the output format is handled by the robust parser,
  and its parse-failure rate is reported — not hidden.

## Deliverables

- [ ] Frozen `prompts/registry.json` (or similar) committed + version tagged.
- [ ] Per-model wrapping notes in `model_matrix.md`.
- [ ] Tier rubric finalized and cross-referenced with annotation protocol.
