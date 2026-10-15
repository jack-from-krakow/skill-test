---
name: married-auto-large-foreign-income
description: "Car loan for married applicants (spouse in the household), requested amount ABOVE 50,000 PLN, applicant earning in EUR from an employer abroad."
---

# Procedure MARRIED_AUTO_LARGE_FOREIGN_INCOME: Car loan above 50,000 PLN for a married couple, applicant earning in EUR from an employer abroad

## When to use
Use this procedure when the applicant is married (a spouse is listed in the application), the product is a car loan, the requested amount is strictly greater than 50,000 PLN and the applicant is earning in EUR from an employer abroad.

## Why the procedure looks like this
Large car loans for married couples are underwritten as joint loans: both spouses are co-borrowers, so the spouse's full base income counts (bonuses at 50% for both) and both credit histories are checked. The vehicle is pledged with a stricter LTV than for single applicants because joint applications typically finance more expensive cars that depreciate faster.

## Applicant's employment
The applicant is paid in EUR by an employer abroad while the loan is in PLN. Convert the applicant's EUR amounts to PLN at the rate quoted in the application, then recognise 85% of the result to cover currency risk; an extra 100 bps is added to the stress test.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `MARRIED_AUTO_LARGE_FOREIGN_INCOME`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 85% x ((applicant base income + 50% of applicant bonus income, both converted from EUR at the quoted rate)) + 100% x (spouse base income + 50% of spouse bonus income). All amounts are monthly net PLN.
- `living_costs` = 2 adults x 1000 PLN + number of dependent children x 600 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits + spouse existing installments + 5% of spouse credit-card limits.
- `dti_limit`: `0.48`
- `stress_test_bps`: `300`
- `collateral_type`: `vehicle`, `collateral_value`: the vehicle price from the application, `ltv_limit`: `0.85`
- `scoring_model`: `RETAIL_STD_JOINT_FX`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `SPOUSE_INCOME_STATEMENT`, `VEHICLE_INVOICE`, `BANK_STATEMENTS_3M`, `FOREIGN_EMPLOYMENT_CONTRACT`, `TAX_RESIDENCY_CERT`
- `extra_checks`: `BIK_APPLICANT`, `BIK_SPOUSE`, `VEHICLE_HISTORY`, `FX_RISK_REVIEW`

## Common mistakes
- Spouse income counts at 100% here (unlike small married car loans).
- LTV limit is 0.85, not 0.90.
- First convert applicant base and bonus income from EUR to PLN at the quoted rate, then apply the counted bonus share, then the 85% haircut.
- Applicant installments and card limits are already in PLN.
- The spouse (if any) earns in PLN; no conversion or haircut for the spouse.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
