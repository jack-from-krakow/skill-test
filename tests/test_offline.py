"""Offline checks: no API key needed."""

import json

from langchain_core.messages import HumanMessage

from skilltest import engine
from skilltest.agents import BUILDERS
from skilltest.cases import sample_cases
from skilltest.engine import EngineArgs, run_engine
from skilltest.fake_model import ScriptedModel
from skilltest.metrics import grade
from skilltest.procedures import BY_CODE, PROCEDURES
from skilltest.prompts import procedure_bodies, system_prompt_a, system_prompt_b
from skilltest.render_skills import SKILLS_DIR, render


CASES = sample_cases(15, 1234)


def test_80_distinct_procedures():
    assert len(PROCEDURES) == 80 == len(BY_CODE)


def test_sampling_is_reproducible_and_distinct():
    a, b = sample_cases(15, 99), sample_cases(15, 99)
    assert [c["prompt"] for c in a] == [c["prompt"] for c in b]
    assert len({c["procedure_code"] for c in a}) == 15
    assert [c["prompt"] for c in sample_cases(15, 100)] != [c["prompt"] for c in a]


def test_every_procedure_generates_a_valid_case():
    import random

    from skilltest.cases import generate_case

    rng = random.Random(0)
    for p in PROCEDURES:
        c = generate_case(p, rng, "t")
        assert c["procedure_code"] == p.code
        run_engine(EngineArgs(**c["expected"]))


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
    c = CASES[0]
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
    assert reads and CASES[3]["procedure_code"] in reads[0].content
    assert len(engine.CALL_LOG) == 1


def test_tool_takes_at_least_20ms():
    import time

    t0 = time.perf_counter()
    engine.credit_analysis_engine.invoke(CASES[0]["expected"])
    assert time.perf_counter() - t0 >= 0.020


def test_variant_c_has_only_read_file_and_engine():
    from skilltest.dump_context import CapturingAnthropic

    case = CASES[2]
    skill = f"/skills/{BY_CODE[case['procedure_code']].skill_name}/SKILL.md"
    engine.CALL_LOG.clear()
    model = CapturingAnthropic(model="claude-haiku-5-5", case=case, skill_path=skill, payloads=[])
    BUILDERS["C"](model).invoke({"messages": [HumanMessage(case["prompt"])]})
    assert len(model.payloads) == 3
    assert sorted(t["name"] for t in model.payloads[0]["tools"]) == ["credit_analysis_engine", "read_file"]
    assert grade(engine.CALL_LOG[0], case["expected"])["fully_correct"]
