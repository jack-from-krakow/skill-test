---
name: single-auto-large
description: "Credit procedure SINGLE_AUTO_LARGE: car loan for single applicants (not married), requested amount ABOVE 50,000 PLN. Read before calling credit_analysis_engine for such an application."
---

# Procedure SINGLE_AUTO_LARGE: Car loan above 50,000 PLN for a single applicant

## When to use
Use this procedure when the applicant is single (no spouse), the product is a car loan and the requested amount is strictly greater than 50,000 PLN.

## Why the procedure looks like this
Larger car loans for a single applicant carry a meaningful loss given default, so the bank takes a registration pledge on the vehicle and verifies the car's history (no previous total loss, no outstanding lien). Variable income is only half-counted because a single earner has no second income to absorb a bonus cut, and a 200 bps rate shock is applied to the installment.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_AUTO_LARGE`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = applicant base income + 50% of applicant bonus income. All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1300 PLN + number of dependent children x 600 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits.
- `dti_limit`: `0.45`
- `stress_test_bps`: `200`
- `collateral_type`: `vehicle`, `collateral_value`: the vehicle price from the application, `ltv_limit`: `0.9`
- `scoring_model`: `RETAIL_STD`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `VEHICLE_INVOICE`, `BANK_STATEMENTS_3M`
- `extra_checks`: `BIK_APPLICANT`, `VEHICLE_HISTORY`

## Common mistakes
- Only 50% of the bonus counts.
- Credit-card limits are counted at 5% (not 3% as for small car loans).
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
