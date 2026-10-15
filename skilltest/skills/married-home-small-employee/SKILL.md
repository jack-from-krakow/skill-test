---
name: married-home-small-employee
description: "Home/mortgage loan for married applicants (spouse in the household), requested amount UP TO 50,000 PLN (inclusive), applicant employed on a standard employment contract."
---

# Procedure MARRIED_HOME_SMALL_EMPLOYEE: Home loan up to 50,000 PLN for a married couple, applicant employed on a standard employment contract

## When to use
Use this procedure when the applicant is married (a spouse is listed in the application), the product is a home loan secured on residential property, the requested amount is at most 50,000 PLN (50,000 itself is small) and the applicant is employed on a standard employment contract.

## Why the procedure looks like this
Any loan secured on a married couple's home requires both spouses as co-borrowers, because the mortgage is entered against jointly owned property. Both incomes count in full (bonuses at 50%), both credit histories are checked and a desktop valuation is sufficient for the small amount.

## Applicant's employment
The applicant has a standard employment contract (umowa o pracę), so the income statement issued by the employer is sufficient and no income haircut applies.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `MARRIED_HOME_SMALL_EMPLOYEE`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = applicant base income + 50% of applicant bonus income + 100% x (spouse base income + 50% of spouse bonus income). All amounts are monthly net PLN.
- `living_costs` = 2 adults x 1350 PLN + number of dependent children x 800 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits + spouse existing installments + 5% of spouse credit-card limits.
- `dti_limit`: `0.45`
- `stress_test_bps`: `250`
- `collateral_type`: `property`, `collateral_value`: the property value from the application, `ltv_limit`: `0.8`
- `scoring_model`: `MORTGAGE_LITE_JOINT`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `SPOUSE_INCOME_STATEMENT`, `LAND_REGISTRY_EXTRACT`
- `extra_checks`: `BIK_APPLICANT`, `BIK_SPOUSE`, `PROPERTY_VALUATION`

## Common mistakes
- Both spouses are co-borrowers: spouse income at 100%, spouse obligations included.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
