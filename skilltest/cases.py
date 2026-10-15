"""Random test applications.

``sample_cases(n, seed)`` draws ``n`` distinct procedures out of the 80 and
generates one complete application for each. The same seed always gives the
same cases, so variants A and B within one repetition see identical
applications. Nothing in a prompt names the procedure: the agent has to work
out which one applies (marital status x product x amount x employment).

Applications deliberately contain data that the matching procedure tells the
agent to ignore (bonus of a self-employed applicant, spouse data on a
single-signature product, vehicle price on an unsecured loan, ...).
"""

from __future__ import annotations

import random

from .procedures import EUR_PLN, PROCEDURES, Procedure, expected_arguments, select_procedure

FIRST = ["Tomasz", "Anna", "Piotr", "Karolina", "Marek", "Ewa", "Katarzyna", "Michał", "Paweł", "Magdalena",
         "Krzysztof", "Agnieszka", "Jakub", "Natalia", "Adam", "Joanna", "Robert", "Monika", "Łukasz", "Zofia"]
LAST = ["Nowak", "Wiśniewski", "Zieliński", "Lewandowski", "Wójcik", "Kamiński", "Szymański", "Dąbrowski",
        "Kozłowski", "Jankowski", "Mazur", "Krawczyk", "Piotrowski", "Grabowski", "Pawlak"]

PRODUCT_TEXT = {
    "auto": "car loan",
    "home": "home loan (secured on their residential property)",
    "rev": "revolving credit line",
    "cash": "cash loan (unsecured)",
}
EMPLOYMENT_TEXT = {
    "employee": "employment contract (umowa o pracę), employed in Poland",
    "self_employed": "self-employed, runs a sole proprietorship",
    "civil_contract": "civil-law contracts (umowa zlecenie)",
    "retiree": "retired, receives a pension",
    "foreign_income": "employed abroad, paid in EUR",
}
STORY = {
    "auto": "wants to buy a car",
    "home": "wants a loan secured on their home",
    "rev": "asks for a revolving credit line",
    "cash": "asks for a cash loan",
}


def _amount(rng: random.Random, p: Procedure) -> int:
    if p.size == "small":
        if rng.random() < 0.15:
            return 50_000  # boundary: still "small"
        return rng.randrange(5_000, 50_001, 500)
    hi = {"auto": 220_000, "home": 900_000, "rev": 160_000, "cash": 160_000}[p.product]
    return rng.randrange(50_500, hi + 1, 500)


def _term(rng: random.Random, p: Procedure) -> int:
    if p.product == "rev":
        return 36
    if p.product == "home":
        return rng.choice([120, 180, 240, 300, 360] if p.size == "large" else [60, 84, 96, 120, 180])
    if p.product == "auto":
        return rng.choice([24, 36, 48, 60, 72, 84, 96])
    return rng.choice([12, 24, 36, 48, 60, 84, 120])


def _person(rng: random.Random, eur: bool = False) -> dict:
    div = EUR_PLN if eur else 1.0
    return dict(
        name=f"{rng.choice(FIRST)} {rng.choice(LAST)}",
        base_income=int(round(rng.randrange(4_000, 25_001, 100) / div, -1)),
        bonus_income=int(round(rng.choice([0, 0, 500, 800, 1_200, 2_000, 3_000, 4_500]) / div, -1)),
        installments=rng.choice([0, 0, 200, 350, 500, 800, 1_100, 1_500]),
        card_limits=rng.choice([0, 2_000, 5_000, 8_000, 12_000, 20_000, 30_000]),
    )


def generate_case(p: Procedure, rng: random.Random, case_id: str) -> dict:
    amount = _amount(rng, p)
    case = dict(
        id=case_id, marital=p.marital, product=p.product, employment=p.employment,
        amount=amount, term_months=_term(rng, p),
        applicant=_person(rng, eur=p.employment == "foreign_income"),
        children=rng.choice([0, 0, 1, 1, 2, 3]),
    )
    if p.employment in ("self_employed", "retiree") and case["applicant"]["bonus_income"] == 0:
        case["applicant"]["bonus_income"] = rng.choice([300, 700, 1_500])  # data the procedure ignores
    if p.marital == "married":
        case["spouse"] = _person(rng)
    if p.product == "auto":
        case["vehicle_price"] = int(round(amount * rng.uniform(1.05, 1.5), -2))
    if p.product == "home":
        case["property_value"] = (
            int(round(amount / rng.uniform(0.5, 0.85), -3)) if p.size == "large" else rng.randrange(250_000, 900_001, 5_000)
        )
    if p.product == "rev" or (p.product == "cash" and rng.random() < 0.5):
        case["savings"] = int(round(amount * rng.uniform(0.6, 2.0), -3))
    return finalize(case)


def finalize(case: dict) -> dict:
    case["procedure_code"] = select_procedure(case["marital"], case["product"], case["amount"], case["employment"]).code
    case["prompt"] = render_prompt(case)
    case["expected"] = expected_arguments(case)
    return case


def sample_cases(n: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    procs = rng.sample(PROCEDURES, n)
    return [generate_case(p, rng, f"s{seed}-{i + 1:02d}") for i, p in enumerate(procs)]


def _person_lines(label: str, p: dict, currency: str) -> list[str]:
    return [
        f"{label}: {p['name']}",
        f"  - base net monthly income: {p['base_income']:,} {currency}",
        f"  - average monthly bonus (variable) income: {p.get('bonus_income', 0):,} {currency}",
        f"  - existing loan installments: {p.get('installments', 0):,} PLN / month",
        f"  - total credit-card limits: {p.get('card_limits', 0):,} PLN",
    ]


def render_prompt(case: dict) -> str:
    a = case["applicant"]
    foreign = case["employment"] == "foreign_income"
    lines = [
        f"New credit application. {a['name']} {STORY[case['product']]}.",
        "",
        f"Product: {PRODUCT_TEXT[case['product']]}",
        f"Requested amount: {case['amount']:,} PLN",
        f"Term: {case['term_months']} months",
        f"Marital status: {case['marital']}",
        f"Dependent children: {case.get('children', 0)}",
        f"Applicant's employment: {EMPLOYMENT_TEXT[case['employment']]}",
    ]
    if foreign:
        lines.append(f"Conversion rate: 1 EUR = {EUR_PLN} PLN")
    if "vehicle_price" in case:
        lines.append(f"Vehicle price: {case['vehicle_price']:,} PLN")
    if "property_value" in case:
        lines.append(f"Property value: {case['property_value']:,} PLN")
    if "savings" in case:
        lines.append(f"Savings held at our bank: {case['savings']:,} PLN")
    lines.append("")
    lines += _person_lines("Applicant", a, "EUR" if foreign else "PLN")
    if case.get("spouse"):
        lines += _person_lines("Spouse (employed in Poland)", case["spouse"], "PLN")
    lines += ["", "Please analyse this application and give me the decision."]
    return "\n".join(lines)
