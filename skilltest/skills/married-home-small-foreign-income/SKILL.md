---
name: married-home-small-foreign-income
description: "Home/mortgage loan for married applicants (spouse in the household), requested amount UP TO 50,000 PLN (inclusive), applicant earning in EUR from an employer abroad."
---

# Procedure MARRIED_HOME_SMALL_FOREIGN_INCOME: Home loan up to 50,000 PLN for a married couple, applicant earning in EUR from an employer abroad

## When to use
Use this procedure when the applicant is married (a spouse is listed in the application), the product is a home loan secured on residential property, the requested amount is at most 50,000 PLN (50,000 itself is small) and the applicant is earning in EUR from an employer abroad.

## Why the procedure looks like this
Any loan secured on a married couple's home requires both spouses as co-borrowers, because the mortgage is entered against jointly owned property. Both incomes count in full (bonuses at 50%), both credit histories are checked and a desktop valuation is sufficient for the small amount.

## Applicant's employment
The applicant is paid in EUR by an employer abroad while the loan is in PLN. Convert the applicant's EUR amounts to PLN at the rate quoted in the application, then recognise 85% of the result to cover currency risk; an extra 100 bps is added to the stress test.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `MARRIED_HOME_SMALL_FOREIGN_INCOME`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 85% x ((applicant base income + 50% of applicant bonus income, both converted from EUR at the quoted rate)) + 100% x (spouse base income + 50% of spouse bonus income). All amounts are monthly net PLN.
- `living_costs` = 2 adults x 1300 PLN + number of dependent children x 750 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits + spouse existing installments + 5% of spouse credit-card limits.
- `dti_limit`: `0.45`
- `stress_test_bps`: `350`
- `collateral_type`: `property`, `collateral_value`: the property value from the application, `ltv_limit`: `0.8`
- `scoring_model`: `MORTGAGE_LITE_JOINT_FX`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `SPOUSE_INCOME_STATEMENT`, `LAND_REGISTRY_EXTRACT`, `FOREIGN_EMPLOYMENT_CONTRACT`, `TAX_RESIDENCY_CERT`
- `extra_checks`: `BIK_APPLICANT`, `BIK_SPOUSE`, `PROPERTY_VALUATION`, `FX_RISK_REVIEW`

## Common mistakes
- Both spouses are co-borrowers: spouse income at 100%, spouse obligations included.
- First convert applicant base and bonus income from EUR to PLN at the quoted rate, then apply the counted bonus share, then the 85% haircut.
- Applicant installments and card limits are already in PLN.
- The spouse (if any) earns in PLN; no conversion or haircut for the spouse.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
