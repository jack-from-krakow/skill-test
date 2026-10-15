---
name: single-auto-large-retiree
description: "Car loan for single applicants (not married), requested amount ABOVE 50,000 PLN, applicant a retiree / pensioner."
---

# Procedure SINGLE_AUTO_LARGE_RETIREE: Car loan above 50,000 PLN for a single applicant, applicant a retiree / pensioner

## When to use
Use this procedure when the applicant is single (no spouse), the product is a car loan, the requested amount is strictly greater than 50,000 PLN and the applicant is a retiree / pensioner.

## Why the procedure looks like this
Larger car loans for a single applicant carry a meaningful loss given default, so the bank takes a registration pledge on the vehicle and verifies the car's history (no previous total loss, no outstanding lien). Variable income is only half-counted because a single earner has no second income to absorb a bonus cut, and a 200 bps rate shock is applied to the installment.

## Applicant's employment
Pension income is stable and fully recognised, but a pensioner has no bonus income (any 'bonus' reported is an occasional supplement that is ignored). The loan must be repaid before the applicant turns 80, which is verified by the age/term check.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_AUTO_LARGE_RETIREE`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = applicant base income + 0% of applicant bonus income. All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1400 PLN + number of dependent children x 600 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits.
- `dti_limit`: `0.43`
- `stress_test_bps`: `200`
- `collateral_type`: `vehicle`, `collateral_value`: the vehicle price from the application, `ltv_limit`: `0.9`
- `scoring_model`: `RETAIL_STD_RT`
- `required_documents`: `ID_CARD`, `PENSION_DECISION`, `VEHICLE_INVOICE`, `BANK_STATEMENTS_3M`
- `extra_checks`: `BIK_APPLICANT`, `VEHICLE_HISTORY`, `AGE_TERM_CHECK`

## Common mistakes
- Only 50% of the bonus counts.
- Credit-card limits are counted at 5% (not 3% as for small car loans).
- Bonus income counts at 0% for retirees.
- PENSION_DECISION replaces INCOME_STATEMENT in the documents.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
