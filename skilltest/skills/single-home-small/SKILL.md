---
name: single-home-small
description: "Credit procedure SINGLE_HOME_SMALL: home/mortgage loan for single applicants (not married), requested amount UP TO 50,000 PLN (inclusive). Read before calling credit_analysis_engine for such an application."
---

# Procedure SINGLE_HOME_SMALL: Home loan up to 50,000 PLN for a single applicant

## When to use
Use this procedure when the applicant is single (no spouse), the product is a home loan secured on residential property and the requested amount is at most 50,000 PLN (50,000 itself is small).

## Why the procedure looks like this
Small home loans (renovation, top-ups, small flats) are secured on the property but use a desktop valuation instead of a full appraisal. Recommendation S of the Polish regulator (KNF) requires a 250 bps interest-rate buffer for every loan secured on residential property, and a single household carries higher per-person living costs.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_HOME_SMALL`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = applicant base income + 50% of applicant bonus income. All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1500 PLN + number of dependent children x 800 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits.
- `dti_limit`: `0.4`
- `stress_test_bps`: `250`
- `collateral_type`: `property`, `collateral_value`: the property value from the application, `ltv_limit`: `0.8`
- `scoring_model`: `MORTGAGE_LITE`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `LAND_REGISTRY_EXTRACT`
- `extra_checks`: `BIK_APPLICANT`, `PROPERTY_VALUATION`

## Common mistakes
- Collateral is the property value given in the application (not the requested amount).
- Stress test is 250 bps even though the amount is small.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
