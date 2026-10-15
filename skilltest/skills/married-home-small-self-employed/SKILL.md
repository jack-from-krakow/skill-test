---
name: married-home-small-self-employed
description: "Home/mortgage loan for married applicants (spouse in the household), requested amount UP TO 50,000 PLN (inclusive), applicant self-employed (sole proprietorship)."
---

# Procedure MARRIED_HOME_SMALL_SELF_EMPLOYED: Home loan up to 50,000 PLN for a married couple, applicant self-employed (sole proprietorship)

## When to use
Use this procedure when the applicant is married (a spouse is listed in the application), the product is a home loan secured on residential property, the requested amount is at most 50,000 PLN (50,000 itself is small) and the applicant is self-employed (sole proprietorship).

## Why the procedure looks like this
Any loan secured on a married couple's home requires both spouses as co-borrowers, because the mortgage is entered against jointly owned property. Both incomes count in full (bonuses at 50%), both credit histories are checked and a desktop valuation is sufficient for the small amount.

## Applicant's employment
Self-employed income is volatile and partly reinvested, so the bank recognises only 80% of the average monthly income declared in the tax returns and ignores any 'bonus' or variable part entirely. The business registration is verified in CEIDG and social-security (ZUS) payments must be up to date.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `MARRIED_HOME_SMALL_SELF_EMPLOYED`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 80% x (applicant base income + 0% of applicant bonus income) + 100% x (spouse base income + 0% of spouse bonus income). All amounts are monthly net PLN.
- `living_costs` = 2 adults x 1350 PLN + number of dependent children x 850 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits + spouse existing installments + 5% of spouse credit-card limits.
- `dti_limit`: `0.41`
- `stress_test_bps`: `250`
- `collateral_type`: `property`, `collateral_value`: the property value from the application, `ltv_limit`: `0.8`
- `scoring_model`: `MORTGAGE_LITE_JOINT_SE`
- `required_documents`: `ID_CARD`, `TAX_RETURN_2Y`, `SPOUSE_INCOME_STATEMENT`, `LAND_REGISTRY_EXTRACT`, `ZUS_CERTIFICATE`
- `extra_checks`: `BIK_APPLICANT`, `BIK_SPOUSE`, `PROPERTY_VALUATION`, `CEIDG_CHECK`

## Common mistakes
- Both spouses are co-borrowers: spouse income at 100%, spouse obligations included.
- Bonus/variable income counts at 0% for self-employed applicants, whatever the base procedure says.
- The applicant's recognised income is 80% of base income; the spouse's income is NOT haircut.
- TAX_RETURN_2Y replaces INCOME_STATEMENT in the documents.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
