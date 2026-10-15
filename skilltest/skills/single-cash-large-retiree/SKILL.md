---
name: single-cash-large-retiree
description: "Unsecured cash loan for single applicants (not married), requested amount ABOVE 50,000 PLN, applicant a retiree / pensioner."
---

# Procedure SINGLE_CASH_LARGE_RETIREE: Cash loan above 50,000 PLN for a single applicant, applicant a retiree / pensioner

## When to use
Use this procedure when the applicant is single (no spouse), the product is an unsecured cash loan, the requested amount is strictly greater than 50,000 PLN and the applicant is a retiree / pensioner.

## Why the procedure looks like this
Large unsecured cash loans are the riskiest retail product: no collateral, long terms and frequent use for debt consolidation. Bonus income counts at 50%, a 200 bps rate shock is applied and the purpose of large disbursements is reviewed by the AML team.

## Applicant's employment
Pension income is stable and fully recognised, but a pensioner has no bonus income (any 'bonus' reported is an occasional supplement that is ignored). The loan must be repaid before the applicant turns 80, which is verified by the age/term check.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_CASH_LARGE_RETIREE`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = applicant base income + 0% of applicant bonus income. All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1400 PLN + number of dependent children x 550 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits.
- `dti_limit`: `0.36`
- `stress_test_bps`: `200`
- `collateral_type`: `none`, `collateral_value`: `0`, `ltv_limit`: `null`
- `scoring_model`: `CASH_PRO_RT`
- `required_documents`: `ID_CARD`, `PENSION_DECISION`, `BANK_STATEMENTS_3M`
- `extra_checks`: `BIK_APPLICANT`, `AML_ENHANCED`, `AGE_TERM_CHECK`

## Common mistakes
- No collateral even for large amounts.
- Card limits count at 5%.
- Bonus income counts at 0% for retirees.
- PENSION_DECISION replaces INCOME_STATEMENT in the documents.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
