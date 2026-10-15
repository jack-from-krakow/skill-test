"""Dump the exact Anthropic request of every model call for one case, A and B.

    python -m skilltest.dump_context [case_index] > context.md

No API calls are made: a ChatAnthropic subclass builds the real request
payload (system blocks, tool definitions, messages, cache_control markers)
exactly as it would be sent, records it, and answers with a scripted
"perfect agent" response (B: read skill -> call engine -> answer;
A: call engine -> answer). Token numbers are estimates (chars / 4); the
real numbers per call are in runs.jsonl ("calls").
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from . import cases as cases_mod
from .agents import BUILDERS
from .procedures import BY_CODE

os.environ.setdefault("ANTHROPIC_API_KEY", "dummy-not-used")


class CapturingAnthropic(ChatAnthropic):
    case: dict
    skill_path: str | None = None
    payloads: list = []

    def _generate(self, messages, stop=None, run_manager=None, **kwargs: Any) -> ChatResult:
        self.payloads.append(self._get_request_payload(messages, stop=stop, **kwargs))
        names = [m.name for m in messages if isinstance(m, ToolMessage)]
        if self.skill_path and "read_file" not in names:
            msg = AIMessage(content="", tool_calls=[{"name": "read_file", "args": {"file_path": self.skill_path, "limit": 1000}, "id": "toolu_read"}])
        elif "credit_analysis_engine" not in names:
            msg = AIMessage(content="", tool_calls=[{"name": "credit_analysis_engine", "args": self.case["expected"], "id": "toolu_engine"}])
        else:
            msg = AIMessage(content="Decision: APPROVE ...")
        return ChatResult(generations=[ChatGeneration(message=msg)])


def _text(x: Any) -> str:
    return x if isinstance(x, str) else json.dumps(x, ensure_ascii=False, indent=1)


def _tok(chars: int) -> str:
    return f"{chars:,} znaków ≈ {chars // 4:,} tok."


def _case(index: int) -> dict:
    if hasattr(cases_mod, "CASES"):
        return cases_mod.CASES[index]
    return cases_mod.sample_cases(15, 1234)[index]


def main() -> None:
    idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    case = _case(idx)
    skill = f"/skills/{BY_CODE[case['procedure_code']].skill_name}/SKILL.md"
    out = [f"# Kontekst wywołań modelu: przypadek {case['id']} ({case['procedure_code']})", ""]
    out.append("Szacunek tokenów = znaki / 4 (orientacyjnie; realne liczby per wywołanie są w runs.jsonl).")
    out.append("")
    summary = []
    for variant in ("A", "B"):
        model = CapturingAnthropic(model="claude-haiku-5-5", case=case, skill_path=skill if variant == "B" else None, payloads=[])
        BUILDERS[variant](model).invoke({"messages": [HumanMessage(case["prompt"])]})
        out.append(f"## Wariant {variant}: {len(model.payloads)} wywołania modelu")
        out.append("")
        for n, p in enumerate(model.payloads, 1):
            system = p.get("system")
            sys_chars = len(_text(system)) if system else 0
            tools = p.get("tools") or []
            tool_sizes = [(t.get("name"), len(json.dumps(t, ensure_ascii=False))) for t in tools]
            msgs = p.get("messages") or []
            msg_chars = len(json.dumps(msgs, ensure_ascii=False))
            total = sys_chars + sum(s for _, s in tool_sizes) + msg_chars
            summary.append((variant, n, sys_chars, sum(s for _, s in tool_sizes), len(tools), msg_chars, total))
            out.append(f"### {variant} – wywołanie {n}")
            out.append("")
            out.append("| Składnik | Rozmiar |")
            out.append("|---|---|")
            out.append(f"| system prompt | {_tok(sys_chars)} |")
            out.append(f"| definicje narzędzi ({len(tools)}: {', '.join(n_ for n_, _ in tool_sizes)}) | {_tok(sum(s for _, s in tool_sizes))} |")
            out.append(f"| wiadomości ({len(msgs)}) | {_tok(msg_chars)} |")
            out.append(f"| **razem** | **{_tok(total)}** |")
            out.append("")
            if n == 1:
                out.append("<details><summary>system prompt (pełny)</summary>\n\n```\n" + _text(system) + "\n```\n</details>\n")
                out.append("<details><summary>definicje narzędzi (pełne JSON)</summary>\n\n```json\n" + json.dumps(tools, ensure_ascii=False, indent=1) + "\n```\n</details>\n")
            else:
                out.append("System prompt i narzędzia: identyczne jak w wywołaniu 1 (ten sam prefiks, czytany z cache).")
                out.append("")
            out.append("<details><summary>wiadomości (pełne)</summary>\n\n```json\n" + json.dumps(msgs, ensure_ascii=False, indent=1) + "\n```\n</details>\n")
    head = ["## Podsumowanie", "", "| Wariant | Wywołanie | system | narzędzia | wiadomości | razem |", "|---|---|---|---|---|---|"]
    for v, n, s, t, nt, m, tot in summary:
        head.append(f"| {v} | {n} | {s // 4:,} | {t // 4:,} ({nt}) | {m // 4:,} | **{tot // 4:,}** |")
    for v in ("A", "B"):
        head.append(f"| {v} | **suma** | | | | **{sum(r[6] for r in summary if r[0] == v) // 4:,}** |")
    head.append("")
    print("\n".join(out[:4] + head + out[4:]))


if __name__ == "__main__":
    main()
