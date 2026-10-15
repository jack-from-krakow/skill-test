"""Offline checks: no API key needed."""

import json

from langchain_core.messages import HumanMessage

from skilltest import engine
from skilltest.agents import BUILDERS
from skilltest.cases import CASES
from skilltest.engine import EngineArgs, run_engine
from skilltest.fake_model import ScriptedModel
from skilltest.metrics import grade
from skilltest.procedures import BY_CODE, PROCEDURES
from skilltest.prompts import procedure_bodies, system_prompt_a, system_prompt_b
from skilltest.render_skills import SKILLS_DIR, render


def test_one_case_per_procedure():
    assert len(PROCEDURES) == 12
    assert sorted(c["procedure_code"] for c in CASES) == sorted(BY_CODE)


def test_skill_files_are_up_to_date():
    for p in PROCEDURES:
        assert (SKILLS_DIR / p.skill_name / "SKILL.md").read_text(encoding="utf-8") == render(p), (
            f"{p.skill_name}: run python -m skilltest.render_skills"
        )


def test_same_content_in_both_variants():
    a = system_prompt_a()
    for body in procedure_bodies():
        assert body in a
    assert len(system_prompt_b()) < len(a) / 5


def test_expected_args_are_valid_engine_input():
    for c in CASES:
        run_engine(EngineArgs(**c["expected"]))
        assert grade(c["expected"], c["expected"])["fully_correct"]


def test_grade_catches_wrong_field():
    c = CASES[10]  # married revolving small: spouse must be ignored
    wrong = dict(c["expected"], monthly_income=c["expected"]["monthly_income"] + 4900)
    assert grade(wrong, c["expected"])["wrong_fields"] == ["monthly_income"]


def _run(variant, case):
    skill = f"/skills/{BY_CODE[case['procedure_code']].skill_name}/SKILL.md" if variant == "B" else None
    engine.CALL_LOG.clear()
    out = BUILDERS[variant](ScriptedModel(case=case, skill_path=skill)).invoke({"messages": [HumanMessage(case["prompt"])]})
    return out["messages"]


def test_variant_a_end_to_end_with_scripted_model():
    msgs = _run("A", CASES[0])
    assert len(engine.CALL_LOG) == 1
    assert grade(engine.CALL_LOG[0], CASES[0]["expected"])["fully_correct"]
    assert "Decision" in msgs[-1].content


def test_variant_b_reads_skill_from_disk():
    msgs = _run("B", CASES[3])
    reads = [m for m in msgs if getattr(m, "name", None) == "read_file"]
    assert reads and "MARRIED_AUTO_LARGE" in reads[0].content
    assert len(engine.CALL_LOG) == 1
