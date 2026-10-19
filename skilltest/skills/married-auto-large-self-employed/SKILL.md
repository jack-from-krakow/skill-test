---
name: married-auto-large-self-employed
description: "Car loan for married applicants (spouse in the household), requested amount ABOVE 50,000 PLN, applicant self-employed (sole proprietorship)."
---

# Procedure MARRIED_AUTO_LARGE_SELF_EMPLOYED: Car loan above 50,000 PLN for a married couple, applicant self-employed (sole proprietorship)

## When to use
Use this procedure when the applicant is married (a spouse is listed in the application), the product is a car loan, the requested amount is strictly greater than 50,000 PLN and the applicant is self-employed (sole proprietorship).

## Why the procedure looks like this
Large car loans for married couples are underwritten as joint loans: both spouses are co-borrowers, so the spouse's full base income counts (bonuses at 50% for both) and both credit histories are checked. The vehicle is pledged with a stricter LTV than for single applicants because joint applications typically finance more expensive cars that depreciate faster.

## Applicant's employment
Self-employed income is volatile and partly reinvested, so the bank recognises only 80% of the average monthly income declared in the tax returns and ignores any 'bonus' or variable part entirely. The business registration is verified in CEIDG and social-security (ZUS) payments must be up to date.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `MARRIED_AUTO_LARGE_SELF_EMPLOYED`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 80% x (applicant base income + 0% of applicant bonus income) + 100% x (spouse base income + 0% of spouse bonus income). All amounts are monthly net PLN.
- `living_costs` = 2 adults x 1050 PLN + number of dependent children x 650 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits + spouse existing installments + 5% of spouse credit-card limits.
- `dti_limit`: `0.44`
- `stress_test_bps`: `200`
- `collateral_type`: `vehicle`, `collateral_value`: the vehicle price from the application, `ltv_limit`: `0.85`
- `scoring_model`: `RETAIL_STD_JOINT_SE`
- `required_documents`: `ID_CARD`, `TAX_RETURN_2Y`, `SPOUSE_INCOME_STATEMENT`, `VEHICLE_INVOICE`, `BANK_STATEMENTS_3M`, `ZUS_CERTIFICATE`
- `extra_checks`: `BIK_APPLICANT`, `BIK_SPOUSE`, `VEHICLE_HISTORY`, `CEIDG_CHECK`

## Common mistakes
- Spouse income counts at 100% here (unlike small married car loans).
- LTV limit is 0.85, not 0.90.
- Bonus/variable income counts at 0% for self-employed applicants, whatever the base procedure says.
- The applicant's recognised income is 80% of base income; the spouse's income is NOT haircut.
- TAX_RETURN_2Y replaces INCOME_STATEMENT in the documents.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
