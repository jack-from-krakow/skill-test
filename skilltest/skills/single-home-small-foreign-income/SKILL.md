---
name: single-home-small-foreign-income
description: "Home/mortgage loan for single applicants (not married), requested amount UP TO 50,000 PLN (inclusive), applicant earning in EUR from an employer abroad."
---

# Procedure SINGLE_HOME_SMALL_FOREIGN_INCOME: Home loan up to 50,000 PLN for a single applicant, applicant earning in EUR from an employer abroad

## When to use
Use this procedure when the applicant is single (no spouse), the product is a home loan secured on residential property, the requested amount is at most 50,000 PLN (50,000 itself is small) and the applicant is earning in EUR from an employer abroad.

## Why the procedure looks like this
Small home loans (renovation, top-ups, small flats) are secured on the property but use a desktop valuation instead of a full appraisal. Recommendation S of the Polish regulator (KNF) requires a 250 bps interest-rate buffer for every loan secured on residential property, and a single household carries higher per-person living costs.

## Applicant's employment
The applicant is paid in EUR by an employer abroad while the loan is in PLN. Convert the applicant's EUR amounts to PLN at the rate quoted in the application, then recognise 85% of the result to cover currency risk; an extra 100 bps is added to the stress test.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_HOME_SMALL_FOREIGN_INCOME`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 85% x ((applicant base income + 50% of applicant bonus income, both converted from EUR at the quoted rate)). All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1500 PLN + number of dependent children x 800 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits.
- `dti_limit`: `0.36`
- `stress_test_bps`: `350`
- `collateral_type`: `property`, `collateral_value`: the property value from the application, `ltv_limit`: `0.8`
- `scoring_model`: `MORTGAGE_LITE_FX`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `LAND_REGISTRY_EXTRACT`, `FOREIGN_EMPLOYMENT_CONTRACT`, `TAX_RESIDENCY_CERT`
- `extra_checks`: `BIK_APPLICANT`, `PROPERTY_VALUATION`, `FX_RISK_REVIEW`

## Common mistakes
- Collateral is the property value given in the application (not the requested amount).
- A stress test applies even though the amount is small (KNF Recommendation S).
- First convert applicant base and bonus income from EUR to PLN at the quoted rate, then apply the counted bonus share, then the 85% haircut.
- Applicant installments and card limits are already in PLN.
- The spouse (if any) earns in PLN; no conversion or haircut for the spouse.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
