---
name: married-cash-large-retiree
description: "Unsecured cash loan for married applicants (spouse in the household), requested amount ABOVE 50,000 PLN, applicant a retiree / pensioner."
---

# Procedure MARRIED_CASH_LARGE_RETIREE: Cash loan above 50,000 PLN for a married couple, applicant a retiree / pensioner

## When to use
Use this procedure when the applicant is married (a spouse is listed in the application), the product is an unsecured cash loan, the requested amount is strictly greater than 50,000 PLN and the applicant is a retiree / pensioner.

## Why the procedure looks like this
Large cash loans for married couples are joint loans with both spouses as co-borrowers: both incomes count in full (bonuses at 50%), both credit histories are checked and the AML review of the loan purpose applies.

## Applicant's employment
Pension income is stable and fully recognised, but a pensioner has no bonus income (any 'bonus' reported is an occasional supplement that is ignored). The loan must be repaid before the applicant turns 80, which is verified by the age/term check.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `MARRIED_CASH_LARGE_RETIREE`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = applicant base income + 0% of applicant bonus income + 100% x (spouse base income + 0% of spouse bonus income). All amounts are monthly net PLN.
- `living_costs` = 2 adults x 1100 PLN + number of dependent children x 550 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits + spouse existing installments + 5% of spouse credit-card limits.
- `dti_limit`: `0.4`
- `stress_test_bps`: `200`
- `collateral_type`: `none`, `collateral_value`: `0`, `ltv_limit`: `null`
- `scoring_model`: `CASH_PRO_JOINT_RT`
- `required_documents`: `ID_CARD`, `PENSION_DECISION`, `SPOUSE_INCOME_STATEMENT`, `BANK_STATEMENTS_3M`
- `extra_checks`: `BIK_APPLICANT`, `BIK_SPOUSE`, `AML_ENHANCED`, `AGE_TERM_CHECK`

## Common mistakes
- Both spouses are co-borrowers: spouse income at 100%.
- Bonus income counts at 0% for retirees.
- PENSION_DECISION replaces INCOME_STATEMENT in the documents.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
