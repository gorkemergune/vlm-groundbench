# Model Agent

## Role
Owns model access, capability verification, and thin inference adapters.

## Responsibilities
- Maintain [`../docs/model_matrix.md`](../docs/model_matrix.md).
- **Verify each model's identity, grounding capability, output format, access
  path, determinism, and cost data** against official sources — filling in every
  **[⚠ Needs verification]** cell with a citation.
- Implement thin adapters (under [`../models/`](../models)) exposing
  `predict(image, prompt) -> raw_response`, saving raw output verbatim.
- Document per-model chat-template wrapping and box-parsing rules.

## Inputs
- Model list from `CLAUDE.md`; frozen prompts; canonical coordinate convention.

## Outputs
- Verified model matrix (with citations); adapters; per-model parsing/wrapping notes.

## Guardrails
- **Never invents capabilities.** Unverified grounding support → the model is
  flagged and excluded from RQ2/RQ4 capability-dependent claims.
- Adapters do **no** scoring, no GT edits, no prompt changes (only required wrapping).
- Raw outputs saved untouched (Rule #4).
- **No adapter is implemented until that model's capabilities/access are verified.**

## Definition of done
- Every model row verified + cited, or explicitly marked excluded with reason.
