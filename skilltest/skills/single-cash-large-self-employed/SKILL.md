---
name: single-cash-large-self-employed
description: "Unsecured cash loan for single applicants (not married), requested amount ABOVE 50,000 PLN, applicant self-employed (sole proprietorship)."
---

# Procedure SINGLE_CASH_LARGE_SELF_EMPLOYED: Cash loan above 50,000 PLN for a single applicant, applicant self-employed (sole proprietorship)

## When to use
Use this procedure when the applicant is single (no spouse), the product is an unsecured cash loan, the requested amount is strictly greater than 50,000 PLN and the applicant is self-employed (sole proprietorship).

## Why the procedure looks like this
Large unsecured cash loans are the riskiest retail product: no collateral, long terms and frequent use for debt consolidation. Bonus income counts at 50%, a 200 bps rate shock is applied and the purpose of large disbursements is reviewed by the AML team.

## Applicant's employment
Self-employed income is volatile and partly reinvested, so the bank recognises only 80% of the average monthly income declared in the tax returns and ignores any 'bonus' or variable part entirely. The business registration is verified in CEIDG and social-security (ZUS) payments must be up to date.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_CASH_LARGE_SELF_EMPLOYED`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 80% x (applicant base income + 0% of applicant bonus income). All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1300 PLN + number of dependent children x 650 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits.
- `dti_limit`: `0.33`
- `stress_test_bps`: `200`
- `collateral_type`: `none`, `collateral_value`: `0`, `ltv_limit`: `null`
- `scoring_model`: `CASH_PRO_SE`
- `required_documents`: `ID_CARD`, `TAX_RETURN_2Y`, `BANK_STATEMENTS_3M`, `ZUS_CERTIFICATE`
- `extra_checks`: `BIK_APPLICANT`, `AML_ENHANCED`, `CEIDG_CHECK`

## Common mistakes
- No collateral even for large amounts.
- Card limits count at 5%.
- Bonus/variable income counts at 0% for self-employed applicants, whatever the base procedure says.
- The applicant's recognised income is 80% of base income; the spouse's income is NOT haircut.
- TAX_RETURN_2Y replaces INCOME_STATEMENT in the documents.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
