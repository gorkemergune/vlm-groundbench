"""Adapter interface. Adapters return raw responses verbatim and never score."""
from __future__ import annotations

import abc


class Adapter(abc.ABC):
    """Model-agnostic inference adapter.

    Implementations MUST:
      - return the model's raw response verbatim (for results/raw_outputs/),
      - perform NO scoring, NO GT access, NO coordinate conversion,
      - change only model-required chat/template wrapping, never prompt content.
    """

    #: Human-readable model id (matches docs/model_matrix.md).
    model_id: str = "abstract"

    @abc.abstractmethod
    def predict(self, image, prompt: str):
        """Return the raw model response (string or JSON-serializable)."""
        raise NotImplementedError
