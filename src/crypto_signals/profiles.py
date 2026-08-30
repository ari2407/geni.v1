"""Deployment profiles for low-resource laptops and remote-only models."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Profile:
    name: str
    max_symbols: int
    workers: int
    llm_mode: str
    description: str

PROFILES = {
    "lite": Profile("lite", 20, 1, "off", "CPU/RAM friendly; deterministic agents and public data only"),
    "remote": Profile("remote", 100, 1, "internet", "No local model; optional hosted LLM adviser over HTTPS"),
}

def get_profile(name: str = "lite") -> Profile:
    try:
        return PROFILES[name]
    except KeyError as exc:
        raise ValueError(f"unknown profile: {name}; choose lite or remote") from exc
