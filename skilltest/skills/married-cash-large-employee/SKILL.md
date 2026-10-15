---
name: married-cash-large-employee
description: "Unsecured cash loan for married applicants (spouse in the household), requested amount ABOVE 50,000 PLN, applicant employed on a standard employment contract."
---

# Procedure MARRIED_CASH_LARGE_EMPLOYEE: Cash loan above 50,000 PLN for a married couple, applicant employed on a standard employment contract

## When to use
Use this procedure when the applicant is married (a spouse is listed in the application), the product is an unsecured cash loan, the requested amount is strictly greater than 50,000 PLN and the applicant is employed on a standard employment contract.

## Why the procedure looks like this
Large cash loans for married couples are joint loans with both spouses as co-borrowers: both incomes count in full (bonuses at 50%), both credit histories are checked and the AML review of the loan purpose applies.

## Applicant's employment
The applicant has a standard employment contract (umowa o pracę), so the income statement issued by the employer is sufficient and no income haircut applies.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `MARRIED_CASH_LARGE_EMPLOYEE`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = applicant base income + 50% of applicant bonus income + 100% x (spouse base income + 50% of spouse bonus income). All amounts are monthly net PLN.
- `living_costs` = 2 adults x 1100 PLN + number of dependent children x 550 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits + spouse existing installments + 5% of spouse credit-card limits.
- `dti_limit`: `0.47`
- `stress_test_bps`: `200`
- `collateral_type`: `none`, `collateral_value`: `0`, `ltv_limit`: `null`
- `scoring_model`: `CASH_PRO_JOINT`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `SPOUSE_INCOME_STATEMENT`, `BANK_STATEMENTS_3M`
- `extra_checks`: `BIK_APPLICANT`, `BIK_SPOUSE`, `AML_ENHANCED`

## Common mistakes
- Both spouses are co-borrowers: spouse income at 100%.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
