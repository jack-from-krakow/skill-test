---
name: single-auto-small-retiree
description: "Car loan for single applicants (not married), requested amount UP TO 50,000 PLN (inclusive), applicant a retiree / pensioner."
---

# Procedure SINGLE_AUTO_SMALL_RETIREE: Car loan up to 50,000 PLN for a single applicant, applicant a retiree / pensioner

## When to use
Use this procedure when the applicant is single (no spouse), the product is a car loan, the requested amount is at most 50,000 PLN (50,000 itself is small) and the applicant is a retiree / pensioner.

## Why the procedure looks like this
Small car loans for single applicants are a high-volume, low-touch product. The bank accepts the full variable income because the exposure is short and small, and it does not register the car as collateral: the cost of a registration pledge would exceed the expected loss. Speed matters more than depth here, so only the applicant's credit bureau (BIK) report is checked.

## Applicant's employment
Pension income is stable and fully recognised, but a pensioner has no bonus income (any 'bonus' reported is an occasional supplement that is ignored). The loan must be repaid before the applicant turns 80, which is verified by the age/term check.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_AUTO_SMALL_RETIREE`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = applicant base income + 0% of applicant bonus income. All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1350 PLN + number of dependent children x 600 PLN.
- `monthly_obligations` = applicant existing installments + 3% of applicant credit-card limits.
- `dti_limit`: `0.48`
- `stress_test_bps`: `0`
- `collateral_type`: `none`, `collateral_value`: `0`, `ltv_limit`: `null`
- `scoring_model`: `RETAIL_LITE_RT`
- `required_documents`: `ID_CARD`, `PENSION_DECISION`
- `extra_checks`: `BIK_APPLICANT`, `AGE_TERM_CHECK`

## Common mistakes
- Do not add the vehicle as collateral even if its price is given; collateral_type is 'none' and collateral_value is 0.
- The base product has no stress test; use exactly the stress_test_bps value given below.
- Bonus income counts at 0% for retirees.
- PENSION_DECISION replaces INCOME_STATEMENT in the documents.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
