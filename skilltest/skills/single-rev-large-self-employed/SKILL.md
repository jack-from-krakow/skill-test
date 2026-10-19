---
name: single-rev-large-self-employed
description: "Revolving credit line (overdraft/card limit) for single applicants (not married), requested amount ABOVE 50,000 PLN, applicant self-employed (sole proprietorship)."
---

# Procedure SINGLE_REV_LARGE_SELF_EMPLOYED: Revolving credit line above 50,000 PLN for a single applicant, applicant self-employed (sole proprietorship)

## When to use
Use this procedure when the applicant is single (no spouse), the product is a revolving credit line, the requested amount is strictly greater than 50,000 PLN and the applicant is self-employed (sole proprietorship).

## Why the procedure looks like this
Large revolving lines are offered to affluent single clients against a pledge on their savings held at the bank. The pledge is not loan-to-value tested (there is no LTV limit), but the deposit balance is reported as the collateral value. The 300 bps stress reflects the variable rate on revolving products.

## Applicant's employment
Self-employed income is volatile and partly reinvested, so the bank recognises only 80% of the average monthly income declared in the tax returns and ignores any 'bonus' or variable part entirely. The business registration is verified in CEIDG and social-security (ZUS) payments must be up to date.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_REV_LARGE_SELF_EMPLOYED`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 80% x (applicant base income + 0% of applicant bonus income). All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1200 PLN + number of dependent children x 550 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits.
- `dti_limit`: `0.23`
- `stress_test_bps`: `300`
- `collateral_type`: `deposit_pledge`, `collateral_value`: the savings balance from the application, `ltv_limit`: `null`
- `scoring_model`: `REVOLVING_PRO_SE`
- `required_documents`: `ID_CARD`, `TAX_RETURN_2Y`, `BANK_STATEMENTS_6M`, `DEPOSIT_PLEDGE_AGREEMENT`, `ZUS_CERTIFICATE`
- `extra_checks`: `BIK_APPLICANT`, `AML_ENHANCED`, `CEIDG_CHECK`

## Common mistakes
- collateral_value is the applicant's savings balance, not the requested limit.
- ltv_limit is null (deposit pledges are not LTV-tested).
- Bonus/variable income counts at 0% for self-employed applicants, whatever the base procedure says.
- The applicant's recognised income is 80% of base income; the spouse's income is NOT haircut.
- TAX_RETURN_2Y replaces INCOME_STATEMENT in the documents.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
