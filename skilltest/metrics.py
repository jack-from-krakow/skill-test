"""Per-run metric collection and grading."""

from __future__ import annotations

import time
from typing import Any
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

# USD per 1M tokens for claude-haiku-5-5 (Anthropic first-party, prompts <= 100K).
# Cache write (5 min TTL) is 1.25x input, cache read is 0.1x input.
PRICE = {"input": 0.10, "output": 0.50, "cache_write": 0.125, "cache_read": 0.01}


class UsageRecorder(BaseCallbackHandler):
    """Records latency and token usage of every model call in one agent run."""

    def __init__(self) -> None:
        self.calls: list[dict] = []
        self._start: dict[UUID, float] = {}

    def on_chat_model_start(self, serialized: dict, messages: Any, *, run_id: UUID, **kwargs: Any) -> None:
        self._start[run_id] = time.perf_counter()

    def on_llm_end(self, response: LLMResult, *, run_id: UUID, **kwargs: Any) -> None:
        latency = time.perf_counter() - self._start.pop(run_id, time.perf_counter())
        msg = response.generations[0][0].message
        raw = (getattr(msg, "response_metadata", None) or {}).get("usage") or {}
        um = getattr(msg, "usage_metadata", None) or {}
        details = um.get("input_token_details") or {}
        if raw:  # Anthropic's own numbers: input_tokens excludes cached tokens
            uncached = raw.get("input_tokens", 0)
            cache_read = raw.get("cache_read_input_tokens") or 0
            cache_write = raw.get("cache_creation_input_tokens") or 0
            output = raw.get("output_tokens", 0)
        else:  # LangChain's normalised numbers: input_tokens includes cached tokens
            cache_read = details.get("cache_read") or 0
            cache_write = details.get("cache_creation") or 0
            uncached = um.get("input_tokens", 0) - cache_read - cache_write
            output = um.get("output_tokens", 0)
        self.calls.append(
            {
                "latency_s": round(latency, 3),
                "input_uncached": uncached,
                "cache_read": cache_read,
                "cache_write": cache_write,
                "output": output,
                "tool_calls": [tc["name"] for tc in getattr(msg, "tool_calls", []) or []],
                "stop_reason": (getattr(msg, "response_metadata", None) or {}).get("stop_reason"),
            }
        )

    def totals(self) -> dict:
        t = {k: sum(c[k] for c in self.calls) for k in ("input_uncached", "cache_read", "cache_write", "output")}
        t["input_total"] = t["input_uncached"] + t["cache_read"] + t["cache_write"]
        t["llm_calls"] = len(self.calls)
        t["llm_latency_s"] = round(sum(c["latency_s"] for c in self.calls), 3)
        t["cost_usd"] = round(
            (
                t["input_uncached"] * PRICE["input"]
                + t["cache_write"] * PRICE["cache_write"]
                + t["cache_read"] * PRICE["cache_read"]
                + t["output"] * PRICE["output"]
            )
            / 1e6,
            6,
        )
        return t


def _num_ok(got: Any, want: float) -> bool:
    try:
        return abs(float(got) - float(want)) <= max(1.0, 0.005 * abs(float(want)))
    except (TypeError, ValueError):
        return False


def grade(call: dict | None, expected: dict) -> dict:
    """Field-by-field comparison of the engine arguments with the answer key."""
    if call is None:
        return {"fields_ok": 0, "fields_total": len(expected), "fully_correct": False, "wrong_fields": list(expected)}
    wrong = []
    for key, want in expected.items():
        got = call.get(key)
        if isinstance(want, list):
            ok = sorted(got or []) == sorted(want)
        elif want is None:
            ok = got in (None, 0)
        elif isinstance(want, (int, float)) and not isinstance(want, bool):
            ok = _num_ok(got, want)
        else:
            ok = got == want
        if not ok:
            wrong.append(key)
    return {
        "fields_ok": len(expected) - len(wrong),
        "fields_total": len(expected),
        "fully_correct": not wrong,
        "wrong_fields": wrong,
    }
