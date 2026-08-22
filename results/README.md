# results/

**Raw and derived outputs are kept strictly separate** (CLAUDE.md Rules #4, #5, #7).

```
results/
├── raw_outputs/   # verbatim model responses + run manifests. NEVER edited (Rule #4).
└── metrics/       # metrics computed deterministically from raw_outputs (Rule #5).
```

- `raw_outputs/<run_id>/` — one dir per run: the exact model responses plus
  `manifest.json` (protocol version, model revision, split hash, seed, env hash,
  git commit). Immutable.
- `metrics/<run_id>/` — IoU, mAP, P/R/F1, hallucination rate, latency, cost,
  and CIs. **Fully recomputable from `raw_outputs/`** (Rule #7).

Never manually edit anything here (Rule #6). Metrics are produced only by the
Evaluation agent's deterministic evaluator.
