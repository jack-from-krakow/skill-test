---
name: married-home-large-self-employed
description: "Home/mortgage loan for married applicants (spouse in the household), requested amount ABOVE 50,000 PLN, applicant self-employed (sole proprietorship)."
---

# Procedure MARRIED_HOME_LARGE_SELF_EMPLOYED: Home loan above 50,000 PLN for a married couple, applicant self-employed (sole proprietorship)

## When to use
Use this procedure when the applicant is married (a spouse is listed in the application), the product is a home loan secured on residential property, the requested amount is strictly greater than 50,000 PLN and the applicant is self-employed (sole proprietorship).

## Why the procedure looks like this
The flagship joint mortgage. Two incomes justify a slightly higher LTV (0.85, with low-down-payment insurance priced separately) but variable income is ignored for both spouses. The marriage certificate is required to confirm the property regime, and the full appraisal plus enhanced AML review apply as for every large mortgage.

## Applicant's employment
Self-employed income is volatile and partly reinvested, so the bank recognises only 80% of the average monthly income declared in the tax returns and ignores any 'bonus' or variable part entirely. The business registration is verified in CEIDG and social-security (ZUS) payments must be up to date.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `MARRIED_HOME_LARGE_SELF_EMPLOYED`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 80% x (applicant base income + 0% of applicant bonus income) + 100% x (spouse base income + 0% of spouse bonus income). All amounts are monthly net PLN.
- `living_costs` = 2 adults x 1200 PLN + number of dependent children x 800 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits + spouse existing installments + 5% of spouse credit-card limits.
- `dti_limit`: `0.37`
- `stress_test_bps`: `400`
- `collateral_type`: `property`, `collateral_value`: the property value from the application, `ltv_limit`: `0.85`
- `scoring_model`: `MORTGAGE_PRO_JOINT_SE`
- `required_documents`: `ID_CARD`, `TAX_RETURN_2Y`, `SPOUSE_INCOME_STATEMENT`, `EMPLOYMENT_CONTRACT`, `LAND_REGISTRY_EXTRACT`, `BANK_STATEMENTS_6M`, `MARRIAGE_CERTIFICATE`, `ZUS_CERTIFICATE`
- `extra_checks`: `BIK_APPLICANT`, `BIK_SPOUSE`, `PROPERTY_APPRAISAL`, `AML_ENHANCED`, `CEIDG_CHECK`

## Common mistakes
- Bonus income does not count for either spouse.
- The DTI limit differs from the single-applicant mortgage; use exactly the value given below.
- Bonus/variable income counts at 0% for self-employed applicants, whatever the base procedure says.
- The applicant's recognised income is 80% of base income; the spouse's income is NOT haircut.
- TAX_RETURN_2Y replaces INCOME_STATEMENT in the documents.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
