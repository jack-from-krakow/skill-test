---
name: married-auto-large
description: "Credit procedure MARRIED_AUTO_LARGE: car loan for married applicants (spouse in the household), requested amount ABOVE 50,000 PLN. Read before calling credit_analysis_engine for such an application."
---

# Procedure MARRIED_AUTO_LARGE: Car loan above 50,000 PLN for a married couple

## When to use
Use this procedure when the applicant is married (a spouse is listed in the application), the product is a car loan and the requested amount is strictly greater than 50,000 PLN.

## Why the procedure looks like this
Large car loans for married couples are underwritten as joint loans: both spouses are co-borrowers, so the spouse's full base income counts (bonuses at 50% for both) and both credit histories are checked. The vehicle is pledged with a stricter LTV than for single applicants because joint applications typically finance more expensive cars that depreciate faster.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `MARRIED_AUTO_LARGE`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = applicant base income + 50% of applicant bonus income + 100% x (spouse base income + 50% of spouse bonus income). All amounts are monthly net PLN.
- `living_costs` = 2 adults x 1100 PLN + number of dependent children x 600 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits + spouse existing installments + 5% of spouse credit-card limits.
- `dti_limit`: `0.5`
- `stress_test_bps`: `200`
- `collateral_type`: `vehicle`, `collateral_value`: the vehicle price from the application, `ltv_limit`: `0.85`
- `scoring_model`: `RETAIL_STD_JOINT`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `SPOUSE_INCOME_STATEMENT`, `VEHICLE_INVOICE`, `BANK_STATEMENTS_3M`
- `extra_checks`: `BIK_APPLICANT`, `BIK_SPOUSE`, `VEHICLE_HISTORY`

## Common mistakes
- Spouse income counts at 100% here (unlike small married car loans).
- LTV limit is 0.85, not 0.90.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
