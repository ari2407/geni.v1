"""Optional internet-only LLM adviser with strict signal-provider boundaries.

No model is downloaded locally. The adviser is never a decision maker and has no
functions/tools, wallet, exchange, or Telegram credentials.
"""
from __future__ import annotations
import json
import os
from urllib.request import Request, urlopen

class RemoteAdviser:
    def __init__(self, endpoint: str | None = None, model: str | None = None, token: str | None = None, timeout: int = 12):
        self.endpoint = (endpoint or os.getenv("LLM_BASE_URL", "")).rstrip("/")
        self.model = model or os.getenv("LLM_MODEL", "")
        self.token = token or os.getenv("LLM_API_KEY", "")
        self.timeout = timeout
        if not self.endpoint or not self.model:
            raise ValueError("LLM_BASE_URL and LLM_MODEL are required for remote adviser")

    def advise(self, role: str, evidence: dict) -> str:
        # Keep prompt bounded and explicitly forbid actions outside research.
        prompt = {"role": role, "task": "Return concise market research only. Do not trade, call tools, invent data, or issue an executable order.", "evidence": evidence}
        body = json.dumps({"model": self.model, "temperature": 0, "max_tokens": 300, "messages": [{"role": "user", "content": json.dumps(prompt)}]}).encode()
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = Request(self.endpoint + "/chat/completions", data=body, headers=headers, method="POST")
        with urlopen(request, timeout=self.timeout) as response:
            result = json.loads(response.read())
        try:
            return str(result["choices"][0]["message"]["content"])[:4000]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("remote adviser returned an invalid response") from exc
