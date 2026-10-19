---
name: married-auto-small-self-employed
description: "Car loan for married applicants (spouse in the household), requested amount UP TO 50,000 PLN (inclusive), applicant self-employed (sole proprietorship)."
---

# Procedure MARRIED_AUTO_SMALL_SELF_EMPLOYED: Car loan up to 50,000 PLN for a married couple, applicant self-employed (sole proprietorship)

## When to use
Use this procedure when the applicant is married (a spouse is listed in the application), the product is a car loan, the requested amount is at most 50,000 PLN (50,000 itself is small) and the applicant is self-employed (sole proprietorship).

## Why the procedure looks like this
For a small car loan taken by a married applicant the spouse is not a co-borrower, but Polish family law makes the household jointly exposed, so the spouse signs a consent and half of the spouse's income is recognised. Because household costs are shared, the per-adult living cost is lower than for single applicants and the DTI limit is more generous.

## Applicant's employment
Self-employed income is volatile and partly reinvested, so the bank recognises only 80% of the average monthly income declared in the tax returns and ignores any 'bonus' or variable part entirely. The business registration is verified in CEIDG and social-security (ZUS) payments must be up to date.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `MARRIED_AUTO_SMALL_SELF_EMPLOYED`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 80% x (applicant base income + 0% of applicant bonus income) + 50% x (spouse base income + 0% of spouse bonus income). All amounts are monthly net PLN.
- `living_costs` = 2 adults x 1200 PLN + number of dependent children x 550 PLN.
- `monthly_obligations` = applicant existing installments + 3% of applicant credit-card limits + spouse existing installments + 3% of spouse credit-card limits.
- `dti_limit`: `0.52`
- `stress_test_bps`: `0`
- `collateral_type`: `none`, `collateral_value`: `0`, `ltv_limit`: `null`
- `scoring_model`: `RETAIL_LITE_JOINT_SE`
- `required_documents`: `ID_CARD`, `TAX_RETURN_2Y`, `SPOUSE_CONSENT`, `ZUS_CERTIFICATE`
- `extra_checks`: `BIK_APPLICANT`, `BIK_SPOUSE`, `CEIDG_CHECK`

## Common mistakes
- Spouse income counts at 50% (bonus share applies to the spouse as well), but ALL spouse installments and card limits count.
- Living costs cover two adults plus children.
- Bonus/variable income counts at 0% for self-employed applicants, whatever the base procedure says.
- The applicant's recognised income is 80% of base income; the spouse's income is NOT haircut.
- TAX_RETURN_2Y replaces INCOME_STATEMENT in the documents.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
