---
name: married-rev-small-employee
description: "Revolving credit line (overdraft/card limit) for married applicants (spouse in the household), requested amount UP TO 50,000 PLN (inclusive), applicant employed on a standard employment contract."
---

# Procedure MARRIED_REV_SMALL_EMPLOYEE: Revolving credit line up to 50,000 PLN for a married couple, applicant employed on a standard employment contract

## When to use
Use this procedure when the applicant is married (a spouse is listed in the application), the product is a revolving credit line, the requested amount is at most 50,000 PLN (50,000 itself is small) and the applicant is employed on a standard employment contract.

## Why the procedure looks like this
Small revolving lines are single-signature products even for married clients: the spouse does not sign and is not checked, so neither the spouse's income nor the spouse's obligations are taken into account. The household still has two adults to feed, however, so living costs are computed for the whole household.

## Applicant's employment
The applicant has a standard employment contract (umowa o pracę), so the income statement issued by the employer is sufficient and no income haircut applies.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `MARRIED_REV_SMALL_EMPLOYEE`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = applicant base income + 100% of applicant bonus income (spouse income is NOT counted). All amounts are monthly net PLN.
- `living_costs` = 2 adults x 1300 PLN + number of dependent children x 500 PLN.
- `monthly_obligations` = applicant existing installments + 3% of applicant credit-card limits (spouse installments and card limits are NOT counted).
- `dti_limit`: `0.34`
- `stress_test_bps`: `0`
- `collateral_type`: `none`, `collateral_value`: `0`, `ltv_limit`: `null`
- `scoring_model`: `REVOLVING_LITE`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`
- `extra_checks`: `BIK_APPLICANT`

## Common mistakes
- Ignore spouse income AND spouse obligations entirely, even though they are in the application.
- Living costs still include BOTH adults and all children.
- Use the same scoring model as for singles (REVOLVING_LITE); there is no joint variant.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
