"""Loader for the committed prompt registry (prompts/registry.json).

Read-only helper. Does not author or freeze prompts. The prompted-bbox output
format is LOCKED (Karar B); native prompt wording is TBD-authoring.
"""
from __future__ import annotations

import json
import os

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_REGISTRY_PATH = os.path.join(_REPO_ROOT, "prompts", "registry.json")


def load_registry(path: str | None = None) -> dict:
    with open(path or DEFAULT_REGISTRY_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def output_format_id(registry: dict) -> str:
    return registry["output_format_spec"]["id"]


def entry_by_id(registry: dict, prompt_id: str) -> dict:
    for e in registry["entries"]:
        if e["prompt_id"] == prompt_id:
            return e
    raise KeyError(f"prompt_id {prompt_id!r} not in registry")


def prompted_bbox_entry(registry: dict) -> dict:
    for e in registry["entries"]:
        if e["regime"] == "prompted":
            return e
    raise KeyError("no prompted-regime entry in registry")
