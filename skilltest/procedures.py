"""The 12 credit-analysis procedures (the "skills").

Each procedure is the combination of
    marital status  (single / married)
  x product         (auto / home / revolving)
  x amount          (small: <= 50,000 PLN, large: > 50,000 PLN)

This module is the single source of truth for the procedure parameters. The
SKILL.md files in ``skilltest/skills`` are rendered from it by
``python -m skilltest.render_skills`` and the expected tool arguments used to
grade every run are computed from it as well, so the text the model reads and
the answer key can never drift apart.
"""

from __future__ import annotations

from dataclasses import dataclass, field

LARGE_AMOUNT_THRESHOLD = 50_000  # PLN; strictly greater means "large"

PRODUCT_LABEL = {"auto": "car loan", "home": "home loan", "rev": "revolving credit line"}


@dataclass(frozen=True)
class Procedure:
    marital: str  # "single" | "married"
    product: str  # "auto" | "home" | "rev"
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
    rationale: str  # one paragraph of business context, unique per procedure
    pitfalls: tuple[str, ...] = field(default_factory=tuple)

    @property
    def code(self) -> str:
        return f"{self.marital}_{self.product}_{self.size}".upper()

    @property
    def skill_name(self) -> str:
        return f"{self.marital}-{self.product}-{self.size}"

    @property
    def title(self) -> str:
        amount = "above 50,000 PLN" if self.size == "large" else "up to 50,000 PLN"
        who = "a married couple" if self.marital == "married" else "a single applicant"
        return f"{PRODUCT_LABEL[self.product].capitalize()} {amount} for {who}"


P = Procedure

PROCEDURES: tuple[Procedure, ...] = (
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
            "No stress test for this product: stress_test_bps is 0.",
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
            "Stress test is 250 bps even though the amount is small.",
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
            "DTI limit is 0.42 (not 0.40 as for single applicants).",
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
            "No collateral and no stress test.",
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

BY_CODE = {p.code: p for p in PROCEDURES}
BY_SKILL = {p.skill_name: p for p in PROCEDURES}

ALL_DOCUMENTS = sorted({d for p in PROCEDURES for d in p.required_documents})
ALL_CHECKS = sorted({c for p in PROCEDURES for c in p.extra_checks})
ALL_SCORING_MODELS = sorted({p.scoring_model for p in PROCEDURES})
COLLATERAL_TYPES = ["none", "vehicle", "property", "deposit_pledge"]


def select_procedure(marital: str, product: str, amount: float) -> Procedure:
    size = "large" if amount > LARGE_AMOUNT_THRESHOLD else "small"
    return BY_CODE[f"{marital}_{product}_{size}".upper()]


def expected_arguments(case: dict) -> dict:
    """The exact arguments a correct agent passes to the engine for ``case``."""
    proc = select_procedure(case["marital"], case["product"], case["amount"])
    a = case["applicant"]
    s = case.get("spouse") or {}

    income = a["base_income"] + proc.bonus_share * a.get("bonus_income", 0)
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
