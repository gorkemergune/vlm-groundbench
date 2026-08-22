# Model Matrix

> **Critical integrity note.** Per the task constraints and CLAUDE.md, we do
> **not invent model capabilities**. Every capability claim below is tagged.
> Rows marked **[⚠ Needs verification]** must be confirmed against official model
> cards / papers **before** any RQ2 (specialization) or RQ4 (scale) claim relies
> on them. Do not fill these in from memory or assumption.

## Models under evaluation (from CLAUDE.md)

| Model | Family | Params | Grounding / bbox output | Access (API/local) | Context | Cost data |
|-------|--------|--------|-------------------------|--------------------|---------|-----------|
| Qwen2.5-VL-7B | Qwen-VL | ~7B [⚠ verify] | [⚠ verify — commonly reported to support grounding, confirm output format] | [⚠ verify] | [⚠ verify] | [⚠ verify] |
| Llama 3.2 11B Vision | Llama 3.2 V | ~11B [⚠ verify] | [⚠ verify — vision understanding confirmed; native bbox grounding NOT assumed] | [⚠ verify] | [⚠ verify] | [⚠ verify] |
| Llama 3.2 90B Vision | Llama 3.2 V | ~90B [⚠ verify] | [⚠ verify — same as above] | [⚠ verify] | [⚠ verify] | [⚠ verify] |
| Cosmos Reason | NVIDIA Cosmos [⚠ verify identity] | [⚠ verify] | [⚠ verify — grounding support unknown, do NOT assume] | [⚠ verify] | [⚠ verify] | [⚠ verify] |
| Nemotron 3 Nano Omni | NVIDIA Nemotron [⚠ verify exact name/identity] | [⚠ verify] | [⚠ verify — grounding support unknown, do NOT assume] | [⚠ verify] | [⚠ verify] | [⚠ verify] |

**Nothing in the table above should be treated as verified.** The "family" and
approximate parameter counts are inferred from the model names and are themselves
**[⚠ Needs verification]**. I am explicitly flagging that I cannot confirm the
exact identity, capabilities, or output formats of *Cosmos Reason* and
*Nemotron 3 Nano Omni* from training knowledge.

## Verification checklist (per model, before freeze)

For each model, collect and cite (in this file):
- [ ] Official model card / paper URL + release version/revision id.
- [ ] **Does it natively output bounding boxes?** If yes, in what coordinate
      format (abs vs normalized, xywh vs xyxy)? → drives adapter mapping.
- [ ] Grounding-specialized vs general-purpose classification (for RQ2) **with
      citation**. If unclear → excluded from the RQ2 capability-group test.
- [ ] Parameter count (for RQ4). Same-family scale pairs identified.
- [ ] Access path: hosted API vs local weights; hardware needs if local.
- [ ] Deterministic decoding support (T=0 behavior).
- [ ] Token accounting / pricing availability (for RQ5).
- [ ] Chat template / image-token placement (for `prompt_protocol.md` wrapping).
- [ ] License / terms of use for benchmarking + publishing results.

## RQ dependencies on this table

- **RQ2 (specialization):** needs the verified grounding-specialized vs general
  split. Unverified models are **excluded** from that test, not guessed.
- **RQ4 (scale):** needs verified same-family pairs (e.g., the two Llama 3.2
  Vision sizes appear to be a candidate pair — **[⚠ verify they are truly the
  same architecture at different scale]**).
- **RQ5 (cost/latency):** needs access path + pricing per model.

## Adapter contract (design only — not implemented yet)

Each model gets a thin adapter (under [`../models/`](../models)) implementing a
shared interface:

```
predict(image, prompt) -> raw_response   # verbatim, saved to results/raw_outputs
```

Adapters do **not** score, edit GT, or alter prompts. Box parsing lives in the
evaluation layer with per-model parsing rules documented here once verified.

> No adapters are to be implemented until capabilities and access are verified.
