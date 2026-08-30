"""Provider-agnostic advisory model registry.

Models are optional advisers only. The deterministic risk/manager gates remain
in charge of publishing signals. Remote code and arbitrary model downloads are
never executed automatically.
"""
from __future__ import annotations
from dataclasses import dataclass
import os

@dataclass(frozen=True)
class ModelCandidate:
    name: str
    kind: str
    endpoint_env: str | None
    role: str
    enabled: bool

def candidates() -> tuple[ModelCandidate, ...]:
    # Read environment at call time so service managers and tests can configure
    # providers after importing the module.
    return (
        ModelCandidate("local_rules", "deterministic", None, "baseline", True),
        ModelCandidate("ollama", "local_http", "OLLAMA_BASE_URL", "research_adviser", bool(os.getenv("OLLAMA_BASE_URL"))),
        ModelCandidate("openai_compatible", "remote_http", "LLM_BASE_URL", "research_adviser", bool(os.getenv("LLM_BASE_URL"))),
    )

def enabled_models() -> tuple[ModelCandidate, ...]:
    return tuple(item for item in candidates() if item.enabled)
