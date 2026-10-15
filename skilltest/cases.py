"""Twelve test applications, one per procedure.

Every prompt contains the complete data set. Nothing in a prompt names the
procedure: the agent has to work out which one applies (marital status x
product x amount) and then follow it.
"""

from __future__ import annotations

from .procedures import expected_arguments, select_procedure

CASES: list[dict] = [
    dict(
        id="c01", marital="single", product="auto", amount=38_000, term_months=48,
        applicant=dict(name="Tomasz Nowak", base_income=6_800, bonus_income=900, installments=450, card_limits=5_000),
        children=0, vehicle_price=52_000,
        story="wants to buy a used Skoda Octavia",
    ),
    dict(
        id="c02", marital="single", product="auto", amount=96_000, term_months=72,
        applicant=dict(name="Anna Wiśniewska", base_income=11_500, bonus_income=2_400, installments=0, card_limits=12_000),
        children=1, vehicle_price=118_000,
        story="is buying a new Toyota RAV4 hybrid",
    ),
    dict(
        id="c03", marital="married", product="auto", amount=50_000, term_months=60,
        applicant=dict(name="Piotr Zieliński", base_income=7_200, bonus_income=600, installments=300, card_limits=4_000),
        spouse=dict(name="Karolina Zielińska", base_income=5_400, bonus_income=0, installments=250, card_limits=6_000),
        children=2, vehicle_price=64_000,
        story="needs a family car (Dacia Jogger)",
    ),
    dict(
        id="c04", marital="married", product="auto", amount=145_000, term_months=84,
        applicant=dict(name="Marek Lewandowski", base_income=13_000, bonus_income=3_000, installments=800, card_limits=15_000),
        spouse=dict(name="Ewa Lewandowska", base_income=9_500, bonus_income=1_200, installments=0, card_limits=8_000),
        children=1, vehicle_price=172_000,
        story="is financing a Volvo XC60",
    ),
    dict(
        id="c05", marital="single", product="home", amount=45_000, term_months=120,
        applicant=dict(name="Katarzyna Wójcik", base_income=8_200, bonus_income=1_000, installments=350, card_limits=3_000),
        children=0, property_value=410_000,
        story="wants to renovate the kitchen and bathroom of her flat",
    ),
    dict(
        id="c06", marital="single", product="home", amount=520_000, term_months=300,
        applicant=dict(name="Michał Kamiński", base_income=16_500, bonus_income=4_000, installments=600, card_limits=10_000),
        children=0, property_value=690_000,
        story="is buying a two-room flat in Kraków",
    ),
    dict(
        id="c07", marital="married", product="home", amount=48_500, term_months=96,
        applicant=dict(name="Paweł Szymański", base_income=6_900, bonus_income=1_400, installments=0, card_limits=7_000),
        spouse=dict(name="Magdalena Szymańska", base_income=6_100, bonus_income=800, installments=420, card_limits=2_000),
        children=3, property_value=530_000,
        story="want to install a heat pump and solar panels in their house",
    ),
    dict(
        id="c08", marital="married", product="home", amount=780_000, term_months=360,
        applicant=dict(name="Krzysztof Dąbrowski", base_income=14_800, bonus_income=5_000, installments=1_100, card_limits=20_000),
        spouse=dict(name="Agnieszka Dąbrowska", base_income=12_300, bonus_income=2_000, installments=0, card_limits=10_000),
        children=2, property_value=980_000,
        story="are buying a house near Wieliczka",
    ),
    dict(
        id="c09", marital="single", product="rev", amount=15_000, term_months=36,
        applicant=dict(name="Jakub Kozłowski", base_income=5_600, bonus_income=700, installments=200, card_limits=4_000),
        children=0,
        story="asks for an overdraft limit on his current account",
    ),
    dict(
        id="c10", marital="single", product="rev", amount=120_000, term_months=36,
        applicant=dict(name="Natalia Jankowska", base_income=24_000, bonus_income=6_000, installments=0, card_limits=30_000),
        children=0, savings=150_000,
        story="wants a large revolving line for her consulting business cash flow",
    ),
    dict(
        id="c11", marital="married", product="rev", amount=20_000, term_months=36,
        applicant=dict(name="Adam Mazur", base_income=7_800, bonus_income=1_200, installments=500, card_limits=6_000),
        spouse=dict(name="Joanna Mazur", base_income=4_900, bonus_income=0, installments=900, card_limits=10_000),
        children=1,
        story="asks for a higher credit-card limit",
    ),
    dict(
        id="c12", marital="married", product="rev", amount=90_000, term_months=36,
        applicant=dict(name="Robert Krawczyk", base_income=18_000, bonus_income=4_000, installments=700, card_limits=25_000),
        spouse=dict(name="Monika Krawczyk", base_income=10_000, bonus_income=3_000, installments=300, card_limits=5_000),
        children=2, savings=200_000,
        story="want a revolving line backed by their savings",
    ),
]

PRODUCT_TEXT = {"auto": "car loan", "home": "home loan (secured on their residential property)", "rev": "revolving credit line"}


def _person(label: str, p: dict) -> list[str]:
    return [
        f"{label}: {p['name']}",
        f"  - base net monthly income: {p['base_income']:,} PLN",
        f"  - average monthly bonus (variable) income: {p.get('bonus_income', 0):,} PLN",
        f"  - existing loan installments: {p.get('installments', 0):,} PLN / month",
        f"  - total credit-card limits: {p.get('card_limits', 0):,} PLN",
    ]


def render_prompt(case: dict) -> str:
    a = case["applicant"]
    lines = [
        f"New credit application. {a['name']} {case['story']}.",
        "",
        f"Product: {PRODUCT_TEXT[case['product']]}",
        f"Requested amount: {case['amount']:,} PLN",
        f"Term: {case['term_months']} months",
        f"Marital status: {case['marital']}",
        f"Dependent children: {case.get('children', 0)}",
    ]
    if "vehicle_price" in case:
        lines.append(f"Vehicle price: {case['vehicle_price']:,} PLN")
    if "property_value" in case:
        lines.append(f"Property value: {case['property_value']:,} PLN")
    if "savings" in case:
        lines.append(f"Savings held at our bank: {case['savings']:,} PLN")
    lines.append("")
    lines += _person("Applicant", a)
    if case.get("spouse"):
        lines += _person("Spouse", case["spouse"])
    lines += ["", "Please analyse this application and give me the decision."]
    return "\n".join(lines)


for _c in CASES:
    _c["procedure_code"] = select_procedure(_c["marital"], _c["product"], _c["amount"]).code
    _c["prompt"] = render_prompt(_c)
    _c["expected"] = expected_arguments(_c)
