---
name: married-rev-small-foreign-income
description: "Revolving credit line (overdraft/card limit) for married applicants (spouse in the household), requested amount UP TO 50,000 PLN (inclusive), applicant earning in EUR from an employer abroad."
---

# Procedure MARRIED_REV_SMALL_FOREIGN_INCOME: Revolving credit line up to 50,000 PLN for a married couple, applicant earning in EUR from an employer abroad

## When to use
Use this procedure when the applicant is married (a spouse is listed in the application), the product is a revolving credit line, the requested amount is at most 50,000 PLN (50,000 itself is small) and the applicant is earning in EUR from an employer abroad.

## Why the procedure looks like this
Small revolving lines are single-signature products even for married clients: the spouse does not sign and is not checked, so neither the spouse's income nor the spouse's obligations are taken into account. The household still has two adults to feed, however, so living costs are computed for the whole household.

## Applicant's employment
The applicant is paid in EUR by an employer abroad while the loan is in PLN. Convert the applicant's EUR amounts to PLN at the rate quoted in the application, then recognise 85% of the result to cover currency risk; an extra 100 bps is added to the stress test.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `MARRIED_REV_SMALL_FOREIGN_INCOME`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 85% x ((applicant base income + 100% of applicant bonus income, both converted from EUR at the quoted rate)) (spouse income is NOT counted). All amounts are monthly net PLN.
- `living_costs` = 2 adults x 1200 PLN + number of dependent children x 500 PLN.
- `monthly_obligations` = applicant existing installments + 3% of applicant credit-card limits (spouse installments and card limits are NOT counted).
- `dti_limit`: `0.34`
- `stress_test_bps`: `100`
- `collateral_type`: `none`, `collateral_value`: `0`, `ltv_limit`: `null`
- `scoring_model`: `REVOLVING_LITE_FX`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `FOREIGN_EMPLOYMENT_CONTRACT`, `TAX_RESIDENCY_CERT`
- `extra_checks`: `BIK_APPLICANT`, `FX_RISK_REVIEW`

## Common mistakes
- Ignore spouse income AND spouse obligations entirely, even though they are in the application.
- Living costs still include BOTH adults and all children.
- Use the same scoring model as for singles (REVOLVING_LITE); there is no joint variant.
- First convert applicant base and bonus income from EUR to PLN at the quoted rate, then apply the counted bonus share, then the 85% haircut.
- Applicant installments and card limits are already in PLN.
- The spouse (if any) earns in PLN; no conversion or haircut for the spouse.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
