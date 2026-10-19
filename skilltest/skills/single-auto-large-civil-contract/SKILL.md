---
name: single-auto-large-civil-contract
description: "Car loan for single applicants (not married), requested amount ABOVE 50,000 PLN, applicant working on civil-law contracts (umowa zlecenie / o dzie\u0142o)."
---

# Procedure SINGLE_AUTO_LARGE_CIVIL_CONTRACT: Car loan above 50,000 PLN for a single applicant, applicant working on civil-law contracts (umowa zlecenie / o dzieło)

## When to use
Use this procedure when the applicant is single (no spouse), the product is a car loan, the requested amount is strictly greater than 50,000 PLN and the applicant is working on civil-law contracts (umowa zlecenie / o dzieło).

## Why the procedure looks like this
Larger car loans for a single applicant carry a meaningful loss given default, so the bank takes a registration pledge on the vehicle and verifies the car's history (no previous total loss, no outstanding lien). Variable income is only half-counted because a single earner has no second income to absorb a bonus cut, and a 200 bps rate shock is applied to the installment.

## Applicant's employment
Civil-law contracts (umowa zlecenie / umowa o dzieło) can be terminated at any time and give no paid leave or notice period, so only 70% of the applicant's income is recognised and the bank requires 12 months of contract history and a continuity check.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_AUTO_LARGE_CIVIL_CONTRACT`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 70% x (applicant base income + 50% of applicant bonus income). All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1300 PLN + number of dependent children x 600 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits.
- `dti_limit`: `0.4`
- `stress_test_bps`: `200`
- `collateral_type`: `vehicle`, `collateral_value`: the vehicle price from the application, `ltv_limit`: `0.9`
- `scoring_model`: `RETAIL_STD_CC`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `VEHICLE_INVOICE`, `BANK_STATEMENTS_3M`, `CIVIL_CONTRACTS_12M`
- `extra_checks`: `BIK_APPLICANT`, `VEHICLE_HISTORY`, `INCOME_CONTINUITY`

## Common mistakes
- Only 50% of the bonus counts.
- Credit-card limits are counted at 5% (not 3% as for small car loans).
- The 70% haircut applies to the applicant's base income plus the counted bonus, not to the spouse.
- Keep INCOME_STATEMENT and add CIVIL_CONTRACTS_12M.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
