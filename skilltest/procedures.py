"""The 80 credit-analysis procedures (the "skills").

Each procedure is the combination of
    marital status  (single / married)
  x product         (auto / home / rev = revolving / cash = cash loan)
  x amount          (small: <= 50,000 PLN, large: > 50,000 PLN)
  x employment      (employee / self_employed / civil_contract / retiree / foreign_income)
  = 2 x 4 x 2 x 5 = 80 procedures.

The 16 base procedures (marital x product x amount) define the core rules; the
employment type modifies them (income haircut, bonus treatment, documents,
checks, scoring model). On top of that every procedure gets small,
deterministic per-procedure adjustments of its DTI limit and living costs,
so the numbers of one procedure cannot be derived from its
neighbours: the agent has to read the right one.

This module is the single source of truth. The SKILL.md files in
``skilltest/skills`` are rendered from it by ``python -m skilltest.render_skills``
and the expected tool arguments used for grading are computed from it as well.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, replace

LARGE_AMOUNT_THRESHOLD = 50_000  # PLN; strictly greater means "large"
EUR_PLN = 4.30  # conversion rate quoted in every foreign-income application

PRODUCT_LABEL = {"auto": "car loan", "home": "home loan", "rev": "revolving credit line", "cash": "cash loan"}
EMPLOYMENT_LABEL = {
    "employee": "employed on a standard employment contract",
    "self_employed": "self-employed (sole proprietorship)",
    "civil_contract": "working on civil-law contracts (umowa zlecenie / o dzieło)",
    "retiree": "a retiree / pensioner",
    "foreign_income": "earning in EUR from an employer abroad",
}


@dataclass(frozen=True)
class Procedure:
    marital: str  # "single" | "married"
    product: str  # "auto" | "home" | "rev" | "cash"
    size: str  # "small" | "large"
    bonus_share: float  # share of variable (bonus) income that counts
    spouse_factor: float  # share of spouse income that counts (married only)
    include_spouse_obligations: bool
    adult_cost: int  # monthly living cost per adult in the household
    child_cost: int  # monthly living cost per dependent child
    card_rate: float  # share of credit-card limits counted as monthly obligation
    dti_limit: float
    stress_test_bps: int
    collateral_type: str  # none | vehicle | property | deposit_pledge
    ltv_limit: float | None
    scoring_model: str
    required_documents: tuple[str, ...]
    extra_checks: tuple[str, ...]
    rationale: str  # business context of the base procedure
    pitfalls: tuple[str, ...] = field(default_factory=tuple)
    employment: str = "employee"
    income_factor: float = 1.0  # haircut applied to the applicant's recognised income
    employment_note: str = ""

    @property
    def code(self) -> str:
        return f"{self.marital}_{self.product}_{self.size}_{self.employment}".upper()

    @property
    def skill_name(self) -> str:
        return f"{self.marital}-{self.product}-{self.size}-{self.employment.replace('_', '-')}"

    @property
    def title(self) -> str:
        amount = "above 50,000 PLN" if self.size == "large" else "up to 50,000 PLN"
        who = "a married couple" if self.marital == "married" else "a single applicant"
        return f"{PRODUCT_LABEL[self.product].capitalize()} {amount} for {who}, applicant {EMPLOYMENT_LABEL[self.employment]}"


P = Procedure

BASE_PROCEDURES: tuple[Procedure, ...] = (
    # ---------------------------------------------------------------- AUTO
    P(
        "single", "auto", "small",
        bonus_share=1.0, spouse_factor=0.0, include_spouse_obligations=False,
        adult_cost=1300, child_cost=600, card_rate=0.03,
        dti_limit=0.50, stress_test_bps=0,
        collateral_type="none", ltv_limit=None,
        scoring_model="RETAIL_LITE",
        required_documents=("ID_CARD", "INCOME_STATEMENT"),
        extra_checks=("BIK_APPLICANT",),
        rationale=(
            "Small car loans for single applicants are a high-volume, low-touch product. The bank "
            "accepts the full variable income because the exposure is short and small, and it does "
            "not register the car as collateral: the cost of a registration pledge would exceed the "
            "expected loss. Speed matters more than depth here, so only the applicant's credit "
            "bureau (BIK) report is checked."
        ),
        pitfalls=(
            "Do not add the vehicle as collateral even if its price is given; collateral_type is 'none' and collateral_value is 0.",
            "The base product has no stress test; use exactly the stress_test_bps value given below.",
        ),
    ),
    P(
        "single", "auto", "large",
        bonus_share=0.5, spouse_factor=0.0, include_spouse_obligations=False,
        adult_cost=1300, child_cost=600, card_rate=0.05,
        dti_limit=0.45, stress_test_bps=200,
        collateral_type="vehicle", ltv_limit=0.90,
        scoring_model="RETAIL_STD",
        required_documents=("ID_CARD", "INCOME_STATEMENT", "VEHICLE_INVOICE", "BANK_STATEMENTS_3M"),
        extra_checks=("BIK_APPLICANT", "VEHICLE_HISTORY"),
        rationale=(
            "Larger car loans for a single applicant carry a meaningful loss given default, so the "
            "bank takes a registration pledge on the vehicle and verifies the car's history (no "
            "previous total loss, no outstanding lien). Variable income is only half-counted "
            "because a single earner has no second income to absorb a bonus cut, and a 200 bps "
            "rate shock is applied to the installment."
        ),
        pitfalls=(
            "Only 50% of the bonus counts.",
            "Credit-card limits are counted at 5% (not 3% as for small car loans).",
        ),
    ),
    P(
        "married", "auto", "small",
        bonus_share=1.0, spouse_factor=0.5, include_spouse_obligations=True,
        adult_cost=1100, child_cost=600, card_rate=0.03,
        dti_limit=0.55, stress_test_bps=0,
        collateral_type="none", ltv_limit=None,
        scoring_model="RETAIL_LITE_JOINT",
        required_documents=("ID_CARD", "INCOME_STATEMENT", "SPOUSE_CONSENT"),
        extra_checks=("BIK_APPLICANT", "BIK_SPOUSE"),
        rationale=(
            "For a small car loan taken by a married applicant the spouse is not a co-borrower, but "
            "Polish family law makes the household jointly exposed, so the spouse signs a consent "
            "and half of the spouse's income is recognised. Because household costs are shared, the "
            "per-adult living cost is lower than for single applicants and the DTI limit is more "
            "generous."
        ),
        pitfalls=(
            "Spouse income counts at 50% (bonus share applies to the spouse as well), but ALL spouse installments and card limits count.",
            "Living costs cover two adults plus children.",
        ),
    ),
    P(
        "married", "auto", "large",
        bonus_share=0.5, spouse_factor=1.0, include_spouse_obligations=True,
        adult_cost=1100, child_cost=600, card_rate=0.05,
        dti_limit=0.50, stress_test_bps=200,
        collateral_type="vehicle", ltv_limit=0.85,
        scoring_model="RETAIL_STD_JOINT",
        required_documents=("ID_CARD", "INCOME_STATEMENT", "SPOUSE_INCOME_STATEMENT", "VEHICLE_INVOICE", "BANK_STATEMENTS_3M"),
        extra_checks=("BIK_APPLICANT", "BIK_SPOUSE", "VEHICLE_HISTORY"),
        rationale=(
            "Large car loans for married couples are underwritten as joint loans: both spouses are "
            "co-borrowers, so the spouse's full base income counts (bonuses at 50% for both) and "
            "both credit histories are checked. The vehicle is pledged with a stricter LTV than for "
            "single applicants because joint applications typically finance more expensive cars "
            "that depreciate faster."
        ),
        pitfalls=(
            "Spouse income counts at 100% here (unlike small married car loans).",
            "LTV limit is 0.85, not 0.90.",
        ),
    ),
    # ---------------------------------------------------------------- HOME
    P(
        "single", "home", "small",
        bonus_share=0.5, spouse_factor=0.0, include_spouse_obligations=False,
        adult_cost=1500, child_cost=800, card_rate=0.05,
        dti_limit=0.40, stress_test_bps=250,
        collateral_type="property", ltv_limit=0.80,
        scoring_model="MORTGAGE_LITE",
        required_documents=("ID_CARD", "INCOME_STATEMENT", "LAND_REGISTRY_EXTRACT"),
        extra_checks=("BIK_APPLICANT", "PROPERTY_VALUATION"),
        rationale=(
            "Small home loans (renovation, top-ups, small flats) are secured on the property but "
            "use a desktop valuation instead of a full appraisal. Recommendation S of the Polish "
            "regulator (KNF) requires a 250 bps interest-rate buffer for every loan secured on "
            "residential property, and a single household carries higher per-person living costs."
        ),
        pitfalls=(
            "Collateral is the property value given in the application (not the requested amount).",
            "A stress test applies even though the amount is small (KNF Recommendation S).",
        ),
    ),
    P(
        "single", "home", "large",
        bonus_share=0.0, spouse_factor=0.0, include_spouse_obligations=False,
        adult_cost=1500, child_cost=800, card_rate=0.05,
        dti_limit=0.40, stress_test_bps=400,
        collateral_type="property", ltv_limit=0.80,
        scoring_model="MORTGAGE_PRO",
        required_documents=("ID_CARD", "INCOME_STATEMENT", "EMPLOYMENT_CONTRACT", "LAND_REGISTRY_EXTRACT", "BANK_STATEMENTS_6M"),
        extra_checks=("BIK_APPLICANT", "PROPERTY_APPRAISAL", "AML_ENHANCED"),
        rationale=(
            "A full mortgage for a single applicant is a 20-30 year exposure to one income. "
            "Variable income is ignored entirely, the rate shock is 400 bps and the bank requires a "
            "full on-site appraisal by an accredited valuer. Amounts of this size also trigger "
            "enhanced anti-money-laundering review of the source of the down payment."
        ),
        pitfalls=(
            "Bonus income does not count at all (bonus_share 0).",
            "Use PROPERTY_APPRAISAL, not PROPERTY_VALUATION.",
        ),
    ),
    P(
        "married", "home", "small",
        bonus_share=0.5, spouse_factor=1.0, include_spouse_obligations=True,
        adult_cost=1300, child_cost=800, card_rate=0.05,
        dti_limit=0.45, stress_test_bps=250,
        collateral_type="property", ltv_limit=0.80,
        scoring_model="MORTGAGE_LITE_JOINT",
        required_documents=("ID_CARD", "INCOME_STATEMENT", "SPOUSE_INCOME_STATEMENT", "LAND_REGISTRY_EXTRACT"),
        extra_checks=("BIK_APPLICANT", "BIK_SPOUSE", "PROPERTY_VALUATION"),
        rationale=(
            "Any loan secured on a married couple's home requires both spouses as co-borrowers, "
            "because the mortgage is entered against jointly owned property. Both incomes count in "
            "full (bonuses at 50%), both credit histories are checked and a desktop valuation is "
            "sufficient for the small amount."
        ),
        pitfalls=(
            "Both spouses are co-borrowers: spouse income at 100%, spouse obligations included.",
        ),
    ),
    P(
        "married", "home", "large",
        bonus_share=0.0, spouse_factor=1.0, include_spouse_obligations=True,
        adult_cost=1300, child_cost=800, card_rate=0.05,
        dti_limit=0.42, stress_test_bps=400,
        collateral_type="property", ltv_limit=0.85,
        scoring_model="MORTGAGE_PRO_JOINT",
        required_documents=(
            "ID_CARD", "INCOME_STATEMENT", "SPOUSE_INCOME_STATEMENT", "EMPLOYMENT_CONTRACT",
            "LAND_REGISTRY_EXTRACT", "BANK_STATEMENTS_6M", "MARRIAGE_CERTIFICATE",
        ),
        extra_checks=("BIK_APPLICANT", "BIK_SPOUSE", "PROPERTY_APPRAISAL", "AML_ENHANCED"),
        rationale=(
            "The flagship joint mortgage. Two incomes justify a slightly higher LTV (0.85, with "
            "low-down-payment insurance priced separately) but variable income is ignored for both "
            "spouses. The marriage certificate is required to confirm the property regime, and the "
            "full appraisal plus enhanced AML review apply as for every large mortgage."
        ),
        pitfalls=(
            "Bonus income does not count for either spouse.",
            "The DTI limit differs from the single-applicant mortgage; use exactly the value given below.",
        ),
    ),
    # ---------------------------------------------------------------- REVOLVING
    P(
        "single", "rev", "small",
        bonus_share=1.0, spouse_factor=0.0, include_spouse_obligations=False,
        adult_cost=1200, child_cost=500, card_rate=0.03,
        dti_limit=0.35, stress_test_bps=0,
        collateral_type="none", ltv_limit=None,
        scoring_model="REVOLVING_LITE",
        required_documents=("ID_CARD", "INCOME_STATEMENT"),
        extra_checks=("BIK_APPLICANT",),
        rationale=(
            "A small revolving line (overdraft or card limit) is unsecured and repriced every year, "
            "so no stress test is applied. The DTI limit is tight because the installment the "
            "engine computes for a revolving line is only a proxy for the real utilisation risk."
        ),
        pitfalls=(
            "No collateral.",
        ),
    ),
    P(
        "single", "rev", "large",
        bonus_share=0.5, spouse_factor=0.0, include_spouse_obligations=False,
        adult_cost=1200, child_cost=500, card_rate=0.05,
        dti_limit=0.30, stress_test_bps=300,
        collateral_type="deposit_pledge", ltv_limit=None,
        scoring_model="REVOLVING_PRO",
        required_documents=("ID_CARD", "INCOME_STATEMENT", "BANK_STATEMENTS_6M", "DEPOSIT_PLEDGE_AGREEMENT"),
        extra_checks=("BIK_APPLICANT", "AML_ENHANCED"),
        rationale=(
            "Large revolving lines are offered to affluent single clients against a pledge on their "
            "savings held at the bank. The pledge is not loan-to-value tested (there is no LTV "
            "limit), but the deposit balance is reported as the collateral value. The 300 bps "
            "stress reflects the variable rate on revolving products."
        ),
        pitfalls=(
            "collateral_value is the applicant's savings balance, not the requested limit.",
            "ltv_limit is null (deposit pledges are not LTV-tested).",
        ),
    ),
    P(
        "married", "rev", "small",
        bonus_share=1.0, spouse_factor=0.0, include_spouse_obligations=False,
        adult_cost=1200, child_cost=500, card_rate=0.03,
        dti_limit=0.35, stress_test_bps=0,
        collateral_type="none", ltv_limit=None,
        scoring_model="REVOLVING_LITE",
        required_documents=("ID_CARD", "INCOME_STATEMENT"),
        extra_checks=("BIK_APPLICANT",),
        rationale=(
            "Small revolving lines are single-signature products even for married clients: the "
            "spouse does not sign and is not checked, so neither the spouse's income nor the "
            "spouse's obligations are taken into account. The household still has two adults to "
            "feed, however, so living costs are computed for the whole household."
        ),
        pitfalls=(
            "Ignore spouse income AND spouse obligations entirely, even though they are in the application.",
            "Living costs still include BOTH adults and all children.",
            "Use the same scoring model as for singles (REVOLVING_LITE); there is no joint variant.",
        ),
    ),
    P(
        "married", "rev", "large",
        bonus_share=0.5, spouse_factor=0.7, include_spouse_obligations=True,
        adult_cost=1100, child_cost=500, card_rate=0.05,
        dti_limit=0.33, stress_test_bps=300,
        collateral_type="deposit_pledge", ltv_limit=None,
        scoring_model="REVOLVING_PRO_JOINT",
        required_documents=("ID_CARD", "INCOME_STATEMENT", "SPOUSE_INCOME_STATEMENT", "BANK_STATEMENTS_6M", "DEPOSIT_PLEDGE_AGREEMENT", "SPOUSE_CONSENT"),
        extra_checks=("BIK_APPLICANT", "BIK_SPOUSE", "AML_ENHANCED"),
        rationale=(
            "Large revolving lines for married clients are secured by a pledge on the couple's "
            "savings, which requires the spouse's consent. The spouse becomes a guarantor rather "
            "than a co-borrower, which the bank reflects by recognising 70% of the spouse's income "
            "while counting all of the spouse's obligations."
        ),
        pitfalls=(
            "Spouse income at 70% (after applying the 50% bonus share to the spouse's bonus).",
            "collateral_value is the couple's savings balance.",
        ),
    ),
)

CASH_PROCEDURES: tuple[Procedure, ...] = (
    P(
        "single", "cash", "small",
        bonus_share=1.0, spouse_factor=0.0, include_spouse_obligations=False,
        adult_cost=1300, child_cost=600, card_rate=0.03,
        dti_limit=0.45, stress_test_bps=0,
        collateral_type="none", ltv_limit=None,
        scoring_model="CASH_LITE",
        required_documents=("ID_CARD", "INCOME_STATEMENT"),
        extra_checks=("BIK_APPLICANT",),
        rationale=(
            "Small unsecured cash loans are sold through the mobile app with an automated decision. "
            "The exposure is small and short, so the full bonus counts and no stress test is applied, "
            "but the DTI limit is lower than for car loans because there is no asset behind the loan."
        ),
        pitfalls=("Cash loans are never secured: collateral_type 'none', collateral_value 0.",),
    ),
    P(
        "single", "cash", "large",
        bonus_share=0.5, spouse_factor=0.0, include_spouse_obligations=False,
        adult_cost=1300, child_cost=600, card_rate=0.05,
        dti_limit=0.40, stress_test_bps=200,
        collateral_type="none", ltv_limit=None,
        scoring_model="CASH_PRO",
        required_documents=("ID_CARD", "INCOME_STATEMENT", "BANK_STATEMENTS_3M"),
        extra_checks=("BIK_APPLICANT", "AML_ENHANCED"),
        rationale=(
            "Large unsecured cash loans are the riskiest retail product: no collateral, long terms and "
            "frequent use for debt consolidation. Bonus income counts at 50%, a 200 bps rate shock is "
            "applied and the purpose of large disbursements is reviewed by the AML team."
        ),
        pitfalls=("No collateral even for large amounts.", "Card limits count at 5%."),
    ),
    P(
        "married", "cash", "small",
        bonus_share=1.0, spouse_factor=0.5, include_spouse_obligations=True,
        adult_cost=1100, child_cost=600, card_rate=0.03,
        dti_limit=0.50, stress_test_bps=0,
        collateral_type="none", ltv_limit=None,
        scoring_model="CASH_LITE_JOINT",
        required_documents=("ID_CARD", "INCOME_STATEMENT", "SPOUSE_CONSENT"),
        extra_checks=("BIK_APPLICANT", "BIK_SPOUSE"),
        rationale=(
            "For a small cash loan the spouse only signs a consent; the bank recognises half of the "
            "spouse's income and all of the spouse's obligations, because under Polish family law the "
            "debt burdens the joint household."
        ),
        pitfalls=("Spouse income at 50%, spouse obligations at 100%.",),
    ),
    P(
        "married", "cash", "large",
        bonus_share=0.5, spouse_factor=1.0, include_spouse_obligations=True,
        adult_cost=1100, child_cost=600, card_rate=0.05,
        dti_limit=0.45, stress_test_bps=200,
        collateral_type="none", ltv_limit=None,
        scoring_model="CASH_PRO_JOINT",
        required_documents=("ID_CARD", "INCOME_STATEMENT", "SPOUSE_INCOME_STATEMENT", "BANK_STATEMENTS_3M"),
        extra_checks=("BIK_APPLICANT", "BIK_SPOUSE", "AML_ENHANCED"),
        rationale=(
            "Large cash loans for married couples are joint loans with both spouses as co-borrowers: "
            "both incomes count in full (bonuses at 50%), both credit histories are checked and the AML "
            "review of the loan purpose applies."
        ),
        pitfalls=("Both spouses are co-borrowers: spouse income at 100%.",),
    ),
)


@dataclass(frozen=True)
class Employment:
    name: str
    income_factor: float
    bonus_share: float | None  # None = keep the base procedure's bonus share
    dti_delta: float
    stress_delta: int
    replace_documents: dict  # base document -> replacement
    add_documents: tuple[str, ...]
    add_checks: tuple[str, ...]
    scoring_suffix: str
    note: str
    pitfalls: tuple[str, ...]


EMPLOYMENTS: tuple[Employment, ...] = (
    Employment(
        "employee", 1.0, None, 0.0, 0, {}, (), (), "",
        "The applicant has a standard employment contract (umowa o pracę), so the income statement "
        "issued by the employer is sufficient and no income haircut applies.",
        (),
    ),
    Employment(
        "self_employed", 0.8, 0.0, -0.05, 0,
        {"INCOME_STATEMENT": "TAX_RETURN_2Y"}, ("ZUS_CERTIFICATE",), ("CEIDG_CHECK",), "_SE",
        "Self-employed income is volatile and partly reinvested, so the bank recognises only 80% of "
        "the average monthly income declared in the tax returns and ignores any 'bonus' or variable "
        "part entirely. The business registration is verified in CEIDG and social-security (ZUS) "
        "payments must be up to date.",
        (
            "Bonus/variable income counts at 0% for self-employed applicants, whatever the base procedure says.",
            "The applicant's recognised income is 80% of base income; the spouse's income is NOT haircut.",
            "TAX_RETURN_2Y replaces INCOME_STATEMENT in the documents.",
        ),
    ),
    Employment(
        "civil_contract", 0.7, None, -0.05, 0,
        {}, ("CIVIL_CONTRACTS_12M",), ("INCOME_CONTINUITY",), "_CC",
        "Civil-law contracts (umowa zlecenie / umowa o dzieło) can be terminated at any time and give "
        "no paid leave or notice period, so only 70% of the applicant's income is recognised and the "
        "bank requires 12 months of contract history and a continuity check.",
        (
            "The 70% haircut applies to the applicant's base income plus the counted bonus, not to the spouse.",
            "Keep INCOME_STATEMENT and add CIVIL_CONTRACTS_12M.",
        ),
    ),
    Employment(
        "retiree", 1.0, 0.0, -0.03, 0,
        {"INCOME_STATEMENT": "PENSION_DECISION"}, (), ("AGE_TERM_CHECK",), "_RT",
        "Pension income is stable and fully recognised, but a pensioner has no bonus income (any "
        "'bonus' reported is an occasional supplement that is ignored). The loan must be repaid "
        "before the applicant turns 80, which is verified by the age/term check.",
        (
            "Bonus income counts at 0% for retirees.",
            "PENSION_DECISION replaces INCOME_STATEMENT in the documents.",
        ),
    ),
    Employment(
        "foreign_income", 0.85, None, -0.02, 100,
        {}, ("FOREIGN_EMPLOYMENT_CONTRACT", "TAX_RESIDENCY_CERT"), ("FX_RISK_REVIEW",), "_FX",
        "The applicant is paid in EUR by an employer abroad while the loan is in PLN. Convert the "
        "applicant's EUR amounts to PLN at the rate quoted in the application, then recognise 85% of "
        "the result to cover currency risk; an extra 100 bps is added to the stress test.",
        (
            "First convert applicant base and bonus income from EUR to PLN at the quoted rate, then apply the counted bonus share, then the 85% haircut.",
            "Applicant installments and card limits are already in PLN.",
            "The spouse (if any) earns in PLN; no conversion or haircut for the spouse.",
        ),
    ),
)


def _jitter(code: str, salt: str, options: tuple) -> object:
    h = int(hashlib.sha256(f"{code}:{salt}".encode()).hexdigest(), 16)
    return options[h % len(options)]


def _build(base: Procedure, emp: Employment) -> Procedure:
    docs = tuple(emp.replace_documents.get(d, d) for d in base.required_documents) + emp.add_documents
    proc = replace(
        base,
        employment=emp.name,
        income_factor=emp.income_factor,
        bonus_share=base.bonus_share if emp.bonus_share is None else emp.bonus_share,
        dti_limit=base.dti_limit + emp.dti_delta,
        stress_test_bps=base.stress_test_bps + emp.stress_delta,
        required_documents=docs,
        extra_checks=base.extra_checks + emp.add_checks,
        scoring_model=base.scoring_model + emp.scoring_suffix,
        employment_note=emp.note,
        pitfalls=base.pitfalls + emp.pitfalls,
    )
    code = proc.code
    dti = round(proc.dti_limit + _jitter(code, "dti", (-0.02, -0.01, 0.0, 0.01, 0.02)), 2)
    return replace(
        proc,
        dti_limit=max(dti, 0.2),
        adult_cost=proc.adult_cost + _jitter(code, "adult", (-100, -50, 0, 50, 100)),
        child_cost=proc.child_cost + _jitter(code, "child", (-50, 0, 50)),
    )


PROCEDURES: tuple[Procedure, ...] = tuple(
    _build(base, emp) for base in BASE_PROCEDURES + CASH_PROCEDURES for emp in EMPLOYMENTS
)

BY_CODE = {p.code: p for p in PROCEDURES}
BY_SKILL = {p.skill_name: p for p in PROCEDURES}

ALL_DOCUMENTS = sorted({d for p in PROCEDURES for d in p.required_documents})
ALL_CHECKS = sorted({c for p in PROCEDURES for c in p.extra_checks})
ALL_SCORING_MODELS = sorted({p.scoring_model for p in PROCEDURES})
COLLATERAL_TYPES = ["none", "vehicle", "property", "deposit_pledge"]


def select_procedure(marital: str, product: str, amount: float, employment: str) -> Procedure:
    size = "large" if amount > LARGE_AMOUNT_THRESHOLD else "small"
    return BY_CODE[f"{marital}_{product}_{size}_{employment}".upper()]


def expected_arguments(case: dict) -> dict:
    """The exact arguments a correct agent passes to the engine for ``case``."""
    proc = select_procedure(case["marital"], case["product"], case["amount"], case["employment"])
    a = case["applicant"]
    s = case.get("spouse") or {}
    fx = EUR_PLN if proc.employment == "foreign_income" else 1.0

    income = proc.income_factor * (a["base_income"] * fx + proc.bonus_share * a.get("bonus_income", 0) * fx)
    obligations = a.get("installments", 0) + proc.card_rate * a.get("card_limits", 0)
    if proc.marital == "married":
        income += proc.spouse_factor * (s["base_income"] + proc.bonus_share * s.get("bonus_income", 0))
        if proc.include_spouse_obligations:
            obligations += s.get("installments", 0) + proc.card_rate * s.get("card_limits", 0)

    adults = 2 if proc.marital == "married" else 1
    living = adults * proc.adult_cost + case.get("children", 0) * proc.child_cost

    if proc.collateral_type == "vehicle":
        collateral_value = case["vehicle_price"]
    elif proc.collateral_type == "property":
        collateral_value = case["property_value"]
    elif proc.collateral_type == "deposit_pledge":
        collateral_value = case["savings"]
    else:
        collateral_value = 0

    return {
        "procedure_code": proc.code,
        "requested_amount": case["amount"],
        "term_months": case["term_months"],
        "monthly_income": round(income, 2),
        "living_costs": living,
        "monthly_obligations": round(obligations, 2),
        "dti_limit": proc.dti_limit,
        "stress_test_bps": proc.stress_test_bps,
        "collateral_type": proc.collateral_type,
        "collateral_value": collateral_value,
        "ltv_limit": proc.ltv_limit,
        "scoring_model": proc.scoring_model,
        "required_documents": sorted(proc.required_documents),
        "extra_checks": sorted(proc.extra_checks),
    }
