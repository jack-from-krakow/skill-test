"""System prompts for both variants.

Both variants share the same header; they differ only in where the 12
procedure descriptions live:

* variant A: all procedure bodies are appended to the system prompt,
* variant B: the system prompt stays short and the procedures are skills that
  the agent loads on demand (deepagents SkillsMiddleware lists name +
  description, the agent reads the SKILL.md it needs with ``read_file``).
"""

from __future__ import annotations

from .render_skills import SKILLS_DIR

HEADER = """You are a credit analyst assistant at a Polish retail bank.

For every credit application you receive:
1. Determine which credit procedure applies. There are 80 procedures, one per combination of marital status (single / married), product (car loan / home loan / revolving credit line / cash loan), requested amount (up to 50,000 PLN is small, above 50,000 PLN is large) and the applicant's employment (employee / self-employed / civil-law contracts / retiree / foreign income in EUR).
2. Prepare the arguments for the `credit_analysis_engine` tool exactly as that procedure prescribes.
3. Call `credit_analysis_engine` exactly ONCE.
4. Reply with a short summary of the engine's result.

Work from the data in the application only. Do not ask the user questions."""

SKILLS_HINT = """The 80 credit procedures are available as skills. Before preparing the tool arguments, read the one skill that matches the application (and only that one)."""


def _strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.index("\n---", 3)
        return text[end + 4 :].lstrip()
    return text


def procedure_bodies() -> list[str]:
    return [_strip_frontmatter(p.read_text(encoding="utf-8")) for p in sorted(SKILLS_DIR.glob("*/SKILL.md"))]


def system_prompt_a() -> str:
    return HEADER + "\n\n# Credit procedures\n\n" + "\n\n".join(procedure_bodies())


def system_prompt_b() -> str:
    return HEADER + "\n\n" + SKILLS_HINT
