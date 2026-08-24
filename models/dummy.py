"""Offline DummyAdapter — returns pre-programmed raw responses.

Used ONLY for Phase A offline tests: it exercises the raw-output/parse/eval path
without any network, GPU, model download, or API call. It is not a real model.
"""
from __future__ import annotations

from .base import Adapter


class DummyAdapter(Adapter):
    def __init__(self, model_id: str, scripted_responses: dict[str, object]):
        """scripted_responses maps sample_id -> canned raw_response (verbatim)."""
        self.model_id = model_id
        self._scripted = dict(scripted_responses)

    def predict(self, image, prompt: str):
        # image is expected to carry a sample_id for the offline harness.
        sample_id = image if isinstance(image, str) else getattr(image, "sample_id", None)
        return self._scripted[sample_id]
