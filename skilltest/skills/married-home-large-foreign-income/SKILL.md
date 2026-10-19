---
name: married-home-large-foreign-income
description: "Home/mortgage loan for married applicants (spouse in the household), requested amount ABOVE 50,000 PLN, applicant earning in EUR from an employer abroad."
---

# Procedure MARRIED_HOME_LARGE_FOREIGN_INCOME: Home loan above 50,000 PLN for a married couple, applicant earning in EUR from an employer abroad

## When to use
Use this procedure when the applicant is married (a spouse is listed in the application), the product is a home loan secured on residential property, the requested amount is strictly greater than 50,000 PLN and the applicant is earning in EUR from an employer abroad.

## Why the procedure looks like this
The flagship joint mortgage. Two incomes justify a slightly higher LTV (0.85, with low-down-payment insurance priced separately) but variable income is ignored for both spouses. The marriage certificate is required to confirm the property regime, and the full appraisal plus enhanced AML review apply as for every large mortgage.

## Applicant's employment
The applicant is paid in EUR by an employer abroad while the loan is in PLN. Convert the applicant's EUR amounts to PLN at the rate quoted in the application, then recognise 85% of the result to cover currency risk; an extra 100 bps is added to the stress test.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `MARRIED_HOME_LARGE_FOREIGN_INCOME`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 85% x ((applicant base income + 0% of applicant bonus income, both converted from EUR at the quoted rate)) + 100% x (spouse base income + 0% of spouse bonus income). All amounts are monthly net PLN.
- `living_costs` = 2 adults x 1400 PLN + number of dependent children x 750 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits + spouse existing installments + 5% of spouse credit-card limits.
- `dti_limit`: `0.42`
- `stress_test_bps`: `500`
- `collateral_type`: `property`, `collateral_value`: the property value from the application, `ltv_limit`: `0.85`
- `scoring_model`: `MORTGAGE_PRO_JOINT_FX`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `SPOUSE_INCOME_STATEMENT`, `EMPLOYMENT_CONTRACT`, `LAND_REGISTRY_EXTRACT`, `BANK_STATEMENTS_6M`, `MARRIAGE_CERTIFICATE`, `FOREIGN_EMPLOYMENT_CONTRACT`, `TAX_RESIDENCY_CERT`
- `extra_checks`: `BIK_APPLICANT`, `BIK_SPOUSE`, `PROPERTY_APPRAISAL`, `AML_ENHANCED`, `FX_RISK_REVIEW`

## Common mistakes
- Bonus income does not count for either spouse.
- The DTI limit differs from the single-applicant mortgage; use exactly the value given below.
- First convert applicant base and bonus income from EUR to PLN at the quoted rate, then apply the counted bonus share, then the 85% haircut.
- Applicant installments and card limits are already in PLN.
- The spouse (if any) earns in PLN; no conversion or haircut for the spouse.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
