---
name: single-rev-large-retiree
description: "Revolving credit line (overdraft/card limit) for single applicants (not married), requested amount ABOVE 50,000 PLN, applicant a retiree / pensioner."
---

# Procedure SINGLE_REV_LARGE_RETIREE: Revolving credit line above 50,000 PLN for a single applicant, applicant a retiree / pensioner

## When to use
Use this procedure when the applicant is single (no spouse), the product is a revolving credit line, the requested amount is strictly greater than 50,000 PLN and the applicant is a retiree / pensioner.

## Why the procedure looks like this
Large revolving lines are offered to affluent single clients against a pledge on their savings held at the bank. The pledge is not loan-to-value tested (there is no LTV limit), but the deposit balance is reported as the collateral value. The 300 bps stress reflects the variable rate on revolving products.

## Applicant's employment
Pension income is stable and fully recognised, but a pensioner has no bonus income (any 'bonus' reported is an occasional supplement that is ignored). The loan must be repaid before the applicant turns 80, which is verified by the age/term check.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_REV_LARGE_RETIREE`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = applicant base income + 0% of applicant bonus income. All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1200 PLN + number of dependent children x 550 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits.
- `dti_limit`: `0.29`
- `stress_test_bps`: `300`
- `collateral_type`: `deposit_pledge`, `collateral_value`: the savings balance from the application, `ltv_limit`: `null`
- `scoring_model`: `REVOLVING_PRO_RT`
- `required_documents`: `ID_CARD`, `PENSION_DECISION`, `BANK_STATEMENTS_6M`, `DEPOSIT_PLEDGE_AGREEMENT`
- `extra_checks`: `BIK_APPLICANT`, `AML_ENHANCED`, `AGE_TERM_CHECK`

## Common mistakes
- collateral_value is the applicant's savings balance, not the requested limit.
- ltv_limit is null (deposit pledges are not LTV-tested).
- Bonus income counts at 0% for retirees.
- PENSION_DECISION replaces INCOME_STATEMENT in the documents.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
