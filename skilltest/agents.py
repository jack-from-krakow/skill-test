"""Agent factories for both variants."""

from __future__ import annotations

from langchain.agents import create_agent
from langchain_anthropic.middleware import AnthropicPromptCachingMiddleware
from langchain_core.language_models import BaseChatModel

from .engine import credit_analysis_engine
from .prompts import system_prompt_a, system_prompt_b
from .render_skills import SKILLS_DIR

DEFAULT_MODEL = "claude-haiku-5-5"


def make_model(model: str = DEFAULT_MODEL, effort: str | None = None) -> BaseChatModel:
    from langchain_anthropic import ChatAnthropic

    kwargs = {"model": model, "max_tokens": 8000, "max_retries": 4}
    if effort:
        kwargs["reasoning_effort"] = effort
    return ChatAnthropic(**kwargs)


def build_variant_a(model: BaseChatModel):
    """A: plain tool-calling agent, all 12 procedures in one system prompt.

    The same Anthropic prompt-caching middleware that deepagents installs is
    added here, so the comparison is not skewed by caching being on in B only.
    """
    return create_agent(
        model,
        tools=[credit_analysis_engine],
        system_prompt=system_prompt_a(),
        middleware=[AnthropicPromptCachingMiddleware(unsupported_model_behavior="ignore")],
    )


def build_variant_b(model: BaseChatModel):
    """B: langchain deepagents with the 12 procedures as skills."""
    from deepagents import create_deep_agent
    from deepagents.backends import FilesystemBackend

    backend = FilesystemBackend(root_dir=SKILLS_DIR.parent, virtual_mode=True)
    return create_deep_agent(
        model=model,
        tools=[credit_analysis_engine],
        system_prompt=system_prompt_b(),
        skills=["/skills/"],
        backend=backend,
    )


BUILDERS = {"A": build_variant_a, "B": build_variant_b}
