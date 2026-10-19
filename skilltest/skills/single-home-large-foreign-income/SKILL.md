---
name: single-home-large-foreign-income
description: "Home/mortgage loan for single applicants (not married), requested amount ABOVE 50,000 PLN, applicant earning in EUR from an employer abroad."
---

# Procedure SINGLE_HOME_LARGE_FOREIGN_INCOME: Home loan above 50,000 PLN for a single applicant, applicant earning in EUR from an employer abroad

## When to use
Use this procedure when the applicant is single (no spouse), the product is a home loan secured on residential property, the requested amount is strictly greater than 50,000 PLN and the applicant is earning in EUR from an employer abroad.

## Why the procedure looks like this
A full mortgage for a single applicant is a 20-30 year exposure to one income. Variable income is ignored entirely, the rate shock is 400 bps and the bank requires a full on-site appraisal by an accredited valuer. Amounts of this size also trigger enhanced anti-money-laundering review of the source of the down payment.

## Applicant's employment
The applicant is paid in EUR by an employer abroad while the loan is in PLN. Convert the applicant's EUR amounts to PLN at the rate quoted in the application, then recognise 85% of the result to cover currency risk; an extra 100 bps is added to the stress test.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_HOME_LARGE_FOREIGN_INCOME`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 85% x ((applicant base income + 0% of applicant bonus income, both converted from EUR at the quoted rate)). All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1600 PLN + number of dependent children x 850 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits.
- `dti_limit`: `0.37`
- `stress_test_bps`: `500`
- `collateral_type`: `property`, `collateral_value`: the property value from the application, `ltv_limit`: `0.8`
- `scoring_model`: `MORTGAGE_PRO_FX`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `EMPLOYMENT_CONTRACT`, `LAND_REGISTRY_EXTRACT`, `BANK_STATEMENTS_6M`, `FOREIGN_EMPLOYMENT_CONTRACT`, `TAX_RESIDENCY_CERT`
- `extra_checks`: `BIK_APPLICANT`, `PROPERTY_APPRAISAL`, `AML_ENHANCED`, `FX_RISK_REVIEW`

## Common mistakes
- Bonus income does not count at all (bonus_share 0).
- Use PROPERTY_APPRAISAL, not PROPERTY_VALUATION.
- First convert applicant base and bonus income from EUR to PLN at the quoted rate, then apply the counted bonus share, then the 85% haircut.
- Applicant installments and card limits are already in PLN.
- The spouse (if any) earns in PLN; no conversion or haircut for the spouse.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
