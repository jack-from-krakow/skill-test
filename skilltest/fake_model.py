"""A scripted chat model for dry runs without an API key.

It plays the "perfect agent" (B: read skill -> call engine -> answer;
A: call engine -> answer) so the whole pipeline (agents, tool, metrics,
grading, report) can be exercised offline. Token numbers it reports are
character-based ESTIMATES (chars / 4), never real measurements.
"""

from __future__ import annotations

import json
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult


def _chars(messages: list[BaseMessage]) -> int:
    n = 0
    for m in messages:
        c = m.content
        n += len(c) if isinstance(c, str) else len(json.dumps(c))
    return n


class ScriptedModel(BaseChatModel):
    case: dict
    skill_path: str | None = None  # set for variant B
    tool_schemas_chars: int = 0

    @property
    def _llm_type(self) -> str:
        return "scripted-fake"

    def bind_tools(self, tools: Any, **kwargs: Any):
        from langchain_core.utils.function_calling import convert_to_openai_tool

        self.tool_schemas_chars = sum(len(json.dumps(convert_to_openai_tool(t))) for t in tools)
        return self

    def _generate(self, messages: list[BaseMessage], stop=None, run_manager=None, **kwargs: Any) -> ChatResult:
        tool_msgs = [m for m in messages if isinstance(m, ToolMessage)]
        names = [m.name for m in tool_msgs]
        if self.skill_path and "read_file" not in names:
            msg = AIMessage(content="", tool_calls=[{"name": "read_file", "args": {"file_path": self.skill_path, "limit": 1000}, "id": "call_read"}])
        elif "credit_analysis_engine" not in names:
            msg = AIMessage(content="", tool_calls=[{"name": "credit_analysis_engine", "args": self.case["expected"], "id": "call_engine"}])
        else:
            result = json.loads(tool_msgs[-1].content)
            msg = AIMessage(content=f"Decision: {result['decision']} (DTI after stress {result['dti_after_stress']}).")
        in_tokens = (_chars(messages) + self.tool_schemas_chars) // 4
        out_tokens = len(json.dumps(msg.tool_calls) + str(msg.content)) // 4
        msg.usage_metadata = {
            "input_tokens": in_tokens,
            "output_tokens": out_tokens,
            "total_tokens": in_tokens + out_tokens,
            "input_token_details": {"cache_read": 0, "cache_creation": 0},
        }
        return ChatResult(generations=[ChatGeneration(message=msg)])
