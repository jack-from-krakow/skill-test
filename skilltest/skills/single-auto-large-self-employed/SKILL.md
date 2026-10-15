---
name: single-auto-large-self-employed
description: "Car loan for single applicants (not married), requested amount ABOVE 50,000 PLN, applicant self-employed (sole proprietorship)."
---

# Procedure SINGLE_AUTO_LARGE_SELF_EMPLOYED: Car loan above 50,000 PLN for a single applicant, applicant self-employed (sole proprietorship)

## When to use
Use this procedure when the applicant is single (no spouse), the product is a car loan, the requested amount is strictly greater than 50,000 PLN and the applicant is self-employed (sole proprietorship).

## Why the procedure looks like this
Larger car loans for a single applicant carry a meaningful loss given default, so the bank takes a registration pledge on the vehicle and verifies the car's history (no previous total loss, no outstanding lien). Variable income is only half-counted because a single earner has no second income to absorb a bonus cut, and a 200 bps rate shock is applied to the installment.

## Applicant's employment
Self-employed income is volatile and partly reinvested, so the bank recognises only 80% of the average monthly income declared in the tax returns and ignores any 'bonus' or variable part entirely. The business registration is verified in CEIDG and social-security (ZUS) payments must be up to date.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_AUTO_LARGE_SELF_EMPLOYED`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 80% x (applicant base income + 0% of applicant bonus income). All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1250 PLN + number of dependent children x 600 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits.
- `dti_limit`: `0.4`
- `stress_test_bps`: `200`
- `collateral_type`: `vehicle`, `collateral_value`: the vehicle price from the application, `ltv_limit`: `0.9`
- `scoring_model`: `RETAIL_STD_SE`
- `required_documents`: `ID_CARD`, `TAX_RETURN_2Y`, `VEHICLE_INVOICE`, `BANK_STATEMENTS_3M`, `ZUS_CERTIFICATE`
- `extra_checks`: `BIK_APPLICANT`, `VEHICLE_HISTORY`, `CEIDG_CHECK`

## Common mistakes
- Only 50% of the bonus counts.
- Credit-card limits are counted at 5% (not 3% as for small car loans).
- Bonus/variable income counts at 0% for self-employed applicants, whatever the base procedure says.
- The applicant's recognised income is 80% of base income; the spouse's income is NOT haircut.
- TAX_RETURN_2Y replaces INCOME_STATEMENT in the documents.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
