---
name: married-home-large-employee
description: "Home/mortgage loan for married applicants (spouse in the household), requested amount ABOVE 50,000 PLN, applicant employed on a standard employment contract."
---

# Procedure MARRIED_HOME_LARGE_EMPLOYEE: Home loan above 50,000 PLN for a married couple, applicant employed on a standard employment contract

## When to use
Use this procedure when the applicant is married (a spouse is listed in the application), the product is a home loan secured on residential property, the requested amount is strictly greater than 50,000 PLN and the applicant is employed on a standard employment contract.

## Why the procedure looks like this
The flagship joint mortgage. Two incomes justify a slightly higher LTV (0.85, with low-down-payment insurance priced separately) but variable income is ignored for both spouses. The marriage certificate is required to confirm the property regime, and the full appraisal plus enhanced AML review apply as for every large mortgage.

## Applicant's employment
The applicant has a standard employment contract (umowa o pracę), so the income statement issued by the employer is sufficient and no income haircut applies.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `MARRIED_HOME_LARGE_EMPLOYEE`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = applicant base income + 0% of applicant bonus income + 100% x (spouse base income + 0% of spouse bonus income). All amounts are monthly net PLN.
- `living_costs` = 2 adults x 1300 PLN + number of dependent children x 800 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits + spouse existing installments + 5% of spouse credit-card limits.
- `dti_limit`: `0.43`
- `stress_test_bps`: `400`
- `collateral_type`: `property`, `collateral_value`: the property value from the application, `ltv_limit`: `0.85`
- `scoring_model`: `MORTGAGE_PRO_JOINT`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `SPOUSE_INCOME_STATEMENT`, `EMPLOYMENT_CONTRACT`, `LAND_REGISTRY_EXTRACT`, `BANK_STATEMENTS_6M`, `MARRIAGE_CERTIFICATE`
- `extra_checks`: `BIK_APPLICANT`, `BIK_SPOUSE`, `PROPERTY_APPRAISAL`, `AML_ENHANCED`

## Common mistakes
- Bonus income does not count for either spouse.
- The DTI limit differs from the single-applicant mortgage; use exactly the value given below.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
