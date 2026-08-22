# models/

Thin, model-agnostic **inference adapters** live here.

Contract (design only — **not yet implemented**):
```
predict(image, prompt) -> raw_response   # verbatim; saved to results/raw_outputs/
```

Rules:
- Adapters do **no** scoring, **no** GT edits, and **no** prompt content changes
  (only model-required chat/template wrapping).
- **No adapter is implemented until that model's capabilities and access are
  verified** and cited in [`../docs/model_matrix.md`](../docs/model_matrix.md).
- Capabilities are never invented; unverified grounding support → model excluded
  from RQ2/RQ4 capability-dependent claims.
