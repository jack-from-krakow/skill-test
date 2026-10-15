---
name: single-home-large
description: "Credit procedure SINGLE_HOME_LARGE: home/mortgage loan for single applicants (not married), requested amount ABOVE 50,000 PLN. Read before calling credit_analysis_engine for such an application."
---

# Procedure SINGLE_HOME_LARGE: Home loan above 50,000 PLN for a single applicant

## When to use
Use this procedure when the applicant is single (no spouse), the product is a home loan secured on residential property and the requested amount is strictly greater than 50,000 PLN.

## Why the procedure looks like this
A full mortgage for a single applicant is a 20-30 year exposure to one income. Variable income is ignored entirely, the rate shock is 400 bps and the bank requires a full on-site appraisal by an accredited valuer. Amounts of this size also trigger enhanced anti-money-laundering review of the source of the down payment.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_HOME_LARGE`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = applicant base income + 0% of applicant bonus income. All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1500 PLN + number of dependent children x 800 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits.
- `dti_limit`: `0.4`
- `stress_test_bps`: `400`
- `collateral_type`: `property`, `collateral_value`: the property value from the application, `ltv_limit`: `0.8`
- `scoring_model`: `MORTGAGE_PRO`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `EMPLOYMENT_CONTRACT`, `LAND_REGISTRY_EXTRACT`, `BANK_STATEMENTS_6M`
- `extra_checks`: `BIK_APPLICANT`, `PROPERTY_APPRAISAL`, `AML_ENHANCED`

## Common mistakes
- Bonus income does not count at all (bonus_share 0).
- Use PROPERTY_APPRAISAL, not PROPERTY_VALUATION.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
