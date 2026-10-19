---
name: single-auto-large-foreign-income
description: "Car loan for single applicants (not married), requested amount ABOVE 50,000 PLN, applicant earning in EUR from an employer abroad."
---

# Procedure SINGLE_AUTO_LARGE_FOREIGN_INCOME: Car loan above 50,000 PLN for a single applicant, applicant earning in EUR from an employer abroad

## When to use
Use this procedure when the applicant is single (no spouse), the product is a car loan, the requested amount is strictly greater than 50,000 PLN and the applicant is earning in EUR from an employer abroad.

## Why the procedure looks like this
Larger car loans for a single applicant carry a meaningful loss given default, so the bank takes a registration pledge on the vehicle and verifies the car's history (no previous total loss, no outstanding lien). Variable income is only half-counted because a single earner has no second income to absorb a bonus cut, and a 200 bps rate shock is applied to the installment.

## Applicant's employment
The applicant is paid in EUR by an employer abroad while the loan is in PLN. Convert the applicant's EUR amounts to PLN at the rate quoted in the application, then recognise 85% of the result to cover currency risk; an extra 100 bps is added to the stress test.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_AUTO_LARGE_FOREIGN_INCOME`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 85% x ((applicant base income + 50% of applicant bonus income, both converted from EUR at the quoted rate)). All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1300 PLN + number of dependent children x 550 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits.
- `dti_limit`: `0.41`
- `stress_test_bps`: `300`
- `collateral_type`: `vehicle`, `collateral_value`: the vehicle price from the application, `ltv_limit`: `0.9`
- `scoring_model`: `RETAIL_STD_FX`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `VEHICLE_INVOICE`, `BANK_STATEMENTS_3M`, `FOREIGN_EMPLOYMENT_CONTRACT`, `TAX_RESIDENCY_CERT`
- `extra_checks`: `BIK_APPLICANT`, `VEHICLE_HISTORY`, `FX_RISK_REVIEW`

## Common mistakes
- Only 50% of the bonus counts.
- Credit-card limits are counted at 5% (not 3% as for small car loans).
- First convert applicant base and bonus income from EUR to PLN at the quoted rate, then apply the counted bonus share, then the 85% haircut.
- Applicant installments and card limits are already in PLN.
- The spouse (if any) earns in PLN; no conversion or haircut for the spouse.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
