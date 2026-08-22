# data/

```
data/
├── raw/          # untouched source images — never edited
├── processed/    # scripted, logged preprocessing (resize/normalize)
├── annotations/  # ground-truth boxes + referring expressions — immutable (Rule #1)
└── splits/       # frozen, content-hashed split manifests
```

- **Ground truth is never modified automatically** (CLAUDE.md Rule #1).
  Corrections go through the Annotation agent, are versioned, and logged in
  `annotations/CHANGELOG.md`.
- Large binaries are gitignored; a `MANIFEST.*` with SHA-256 per file is committed
  so the exact dataset is reconstructable.
- See [`../docs/dataset_spec.md`](../docs/dataset_spec.md) and
  [`../docs/annotation_protocol.md`](../docs/annotation_protocol.md).

> No data has been downloaded yet. Licensing must be verified before acquisition.
