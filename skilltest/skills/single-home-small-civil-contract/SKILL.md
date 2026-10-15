---
name: single-home-small-civil-contract
description: "Home/mortgage loan for single applicants (not married), requested amount UP TO 50,000 PLN (inclusive), applicant working on civil-law contracts (umowa zlecenie / o dzie\u0142o)."
---

# Procedure SINGLE_HOME_SMALL_CIVIL_CONTRACT: Home loan up to 50,000 PLN for a single applicant, applicant working on civil-law contracts (umowa zlecenie / o dzieło)

## When to use
Use this procedure when the applicant is single (no spouse), the product is a home loan secured on residential property, the requested amount is at most 50,000 PLN (50,000 itself is small) and the applicant is working on civil-law contracts (umowa zlecenie / o dzieło).

## Why the procedure looks like this
Small home loans (renovation, top-ups, small flats) are secured on the property but use a desktop valuation instead of a full appraisal. Recommendation S of the Polish regulator (KNF) requires a 250 bps interest-rate buffer for every loan secured on residential property, and a single household carries higher per-person living costs.

## Applicant's employment
Civil-law contracts (umowa zlecenie / umowa o dzieło) can be terminated at any time and give no paid leave or notice period, so only 70% of the applicant's income is recognised and the bank requires 12 months of contract history and a continuity check.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_HOME_SMALL_CIVIL_CONTRACT`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 70% x (applicant base income + 50% of applicant bonus income). All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1550 PLN + number of dependent children x 850 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits.
- `dti_limit`: `0.37`
- `stress_test_bps`: `250`
- `collateral_type`: `property`, `collateral_value`: the property value from the application, `ltv_limit`: `0.8`
- `scoring_model`: `MORTGAGE_LITE_CC`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `LAND_REGISTRY_EXTRACT`, `CIVIL_CONTRACTS_12M`
- `extra_checks`: `BIK_APPLICANT`, `PROPERTY_VALUATION`, `INCOME_CONTINUITY`

## Common mistakes
- Collateral is the property value given in the application (not the requested amount).
- A stress test applies even though the amount is small (KNF Recommendation S).
- The 70% haircut applies to the applicant's base income plus the counted bonus, not to the spouse.
- Keep INCOME_STATEMENT and add CIVIL_CONTRACTS_12M.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
