---
name: single-home-large-self-employed
description: "Home/mortgage loan for single applicants (not married), requested amount ABOVE 50,000 PLN, applicant self-employed (sole proprietorship)."
---

# Procedure SINGLE_HOME_LARGE_SELF_EMPLOYED: Home loan above 50,000 PLN for a single applicant, applicant self-employed (sole proprietorship)

## When to use
Use this procedure when the applicant is single (no spouse), the product is a home loan secured on residential property, the requested amount is strictly greater than 50,000 PLN and the applicant is self-employed (sole proprietorship).

## Why the procedure looks like this
A full mortgage for a single applicant is a 20-30 year exposure to one income. Variable income is ignored entirely, the rate shock is 400 bps and the bank requires a full on-site appraisal by an accredited valuer. Amounts of this size also trigger enhanced anti-money-laundering review of the source of the down payment.

## Applicant's employment
Self-employed income is volatile and partly reinvested, so the bank recognises only 80% of the average monthly income declared in the tax returns and ignores any 'bonus' or variable part entirely. The business registration is verified in CEIDG and social-security (ZUS) payments must be up to date.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_HOME_LARGE_SELF_EMPLOYED`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 80% x (applicant base income + 0% of applicant bonus income). All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1600 PLN + number of dependent children x 800 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits.
- `dti_limit`: `0.33`
- `stress_test_bps`: `400`
- `collateral_type`: `property`, `collateral_value`: the property value from the application, `ltv_limit`: `0.8`
- `scoring_model`: `MORTGAGE_PRO_SE`
- `required_documents`: `ID_CARD`, `TAX_RETURN_2Y`, `EMPLOYMENT_CONTRACT`, `LAND_REGISTRY_EXTRACT`, `BANK_STATEMENTS_6M`, `ZUS_CERTIFICATE`
- `extra_checks`: `BIK_APPLICANT`, `PROPERTY_APPRAISAL`, `AML_ENHANCED`, `CEIDG_CHECK`

## Common mistakes
- Bonus income does not count at all (bonus_share 0).
- Use PROPERTY_APPRAISAL, not PROPERTY_VALUATION.
- Bonus/variable income counts at 0% for self-employed applicants, whatever the base procedure says.
- The applicant's recognised income is 80% of base income; the spouse's income is NOT haircut.
- TAX_RETURN_2Y replaces INCOME_STATEMENT in the documents.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
