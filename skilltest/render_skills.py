"""Render skilltest/skills/<name>/SKILL.md from procedures.py.

    python -m skilltest.render_skills
"""

from __future__ import annotations

import json
from pathlib import Path

from .procedures import PROCEDURES, Procedure

SKILLS_DIR = Path(__file__).parent / "skills"


def _pct(x: float) -> str:
    return f"{x * 100:g}%"


def describe(p: Procedure) -> str:
    """Short description: what the skill-selection step sees in variant B."""
    who = "married applicants (spouse in the household)" if p.marital == "married" else "single applicants (not married)"
    amount = "requested amount ABOVE 50,000 PLN" if p.size == "large" else "requested amount UP TO 50,000 PLN (inclusive)"
    product = {"auto": "car loan", "home": "home/mortgage loan", "rev": "revolving credit line (overdraft/card limit)"}[p.product]
    return f"Credit procedure {p.code}: {product} for {who}, {amount}. Read before calling credit_analysis_engine for such an application."


def body(p: Procedure) -> str:
    married = p.marital == "married"
    lines: list[str] = []
    add = lines.append

    add(f"# Procedure {p.code}: {p.title}")
    add("")
    add("## When to use")
    amount = "strictly greater than 50,000 PLN" if p.size == "large" else "at most 50,000 PLN (50,000 itself is small)"
    status = "married (a spouse is listed in the application)" if married else "single (no spouse)"
    product = {"auto": "a car loan", "home": "a home loan secured on residential property", "rev": "a revolving credit line"}[p.product]
    add(f"Use this procedure when the applicant is {status}, the product is {product} and the requested amount is {amount}.")
    add("")
    add("## Why the procedure looks like this")
    add(p.rationale)
    add("")
    add("## How to fill the credit_analysis_engine arguments")
    add(f"- `procedure_code`: `{p.code}`")
    add("- `requested_amount`, `term_months`: copy from the application.")

    inc = f"applicant base income + {_pct(p.bonus_share)} of applicant bonus income"
    if married:
        if p.spouse_factor > 0:
            inc += (
                f" + {_pct(p.spouse_factor)} x (spouse base income + {_pct(p.bonus_share)} of spouse bonus income)"
            )
        else:
            inc += " (spouse income is NOT counted)"
    add(f"- `monthly_income` = {inc}. All amounts are monthly net PLN.")

    adults = "2 adults" if married else "1 adult"
    add(
        f"- `living_costs` = {adults} x {p.adult_cost} PLN + number of dependent children x {p.child_cost} PLN."
    )

    obl = f"applicant existing installments + {_pct(p.card_rate)} of applicant credit-card limits"
    if married:
        if p.include_spouse_obligations:
            obl += f" + spouse existing installments + {_pct(p.card_rate)} of spouse credit-card limits"
        else:
            obl += " (spouse installments and card limits are NOT counted)"
    add(f"- `monthly_obligations` = {obl}.")
    add(f"- `dti_limit`: `{p.dti_limit}`")
    add(f"- `stress_test_bps`: `{p.stress_test_bps}`")

    if p.collateral_type == "none":
        add("- `collateral_type`: `none`, `collateral_value`: `0`, `ltv_limit`: `null`")
    else:
        source = {
            "vehicle": "the vehicle price from the application",
            "property": "the property value from the application",
            "deposit_pledge": "the savings balance from the application" + (" (joint savings of the couple)" if married else ""),
        }[p.collateral_type]
        ltv = "null" if p.ltv_limit is None else str(p.ltv_limit)
        add(f"- `collateral_type`: `{p.collateral_type}`, `collateral_value`: {source}, `ltv_limit`: `{ltv}`")

    add(f"- `scoring_model`: `{p.scoring_model}`")
    add(f"- `required_documents`: {', '.join(f'`{d}`' for d in p.required_documents)}")
    add(f"- `extra_checks`: {', '.join(f'`{c}`' for c in p.extra_checks)}")
    add("")
    add("## Common mistakes")
    for pit in p.pitfalls:
        add(f"- {pit}")
    add("- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to \"double-check\".")
    add("")
    add("## After the call")
    add(
        "Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV "
        "(if any), and the documents the client still has to provide."
    )
    return "\n".join(lines) + "\n"


def render(p: Procedure) -> str:
    return f"---\nname: {p.skill_name}\ndescription: {json.dumps(describe(p))}\n---\n\n{body(p)}"


def main() -> None:
    for p in PROCEDURES:
        d = SKILLS_DIR / p.skill_name
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(render(p), encoding="utf-8")
    print(f"rendered {len(PROCEDURES)} skills into {SKILLS_DIR}")


if __name__ == "__main__":
    main()
