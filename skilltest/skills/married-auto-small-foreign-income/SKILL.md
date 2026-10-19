---
name: married-auto-small-foreign-income
description: "Car loan for married applicants (spouse in the household), requested amount UP TO 50,000 PLN (inclusive), applicant earning in EUR from an employer abroad."
---

# Procedure MARRIED_AUTO_SMALL_FOREIGN_INCOME: Car loan up to 50,000 PLN for a married couple, applicant earning in EUR from an employer abroad

## When to use
Use this procedure when the applicant is married (a spouse is listed in the application), the product is a car loan, the requested amount is at most 50,000 PLN (50,000 itself is small) and the applicant is earning in EUR from an employer abroad.

## Why the procedure looks like this
For a small car loan taken by a married applicant the spouse is not a co-borrower, but Polish family law makes the household jointly exposed, so the spouse signs a consent and half of the spouse's income is recognised. Because household costs are shared, the per-adult living cost is lower than for single applicants and the DTI limit is more generous.

## Applicant's employment
The applicant is paid in EUR by an employer abroad while the loan is in PLN. Convert the applicant's EUR amounts to PLN at the rate quoted in the application, then recognise 85% of the result to cover currency risk; an extra 100 bps is added to the stress test.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `MARRIED_AUTO_SMALL_FOREIGN_INCOME`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 85% x ((applicant base income + 100% of applicant bonus income, both converted from EUR at the quoted rate)) + 50% x (spouse base income + 100% of spouse bonus income). All amounts are monthly net PLN.
- `living_costs` = 2 adults x 1100 PLN + number of dependent children x 600 PLN.
- `monthly_obligations` = applicant existing installments + 3% of applicant credit-card limits + spouse existing installments + 3% of spouse credit-card limits.
- `dti_limit`: `0.55`
- `stress_test_bps`: `100`
- `collateral_type`: `none`, `collateral_value`: `0`, `ltv_limit`: `null`
- `scoring_model`: `RETAIL_LITE_JOINT_FX`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `SPOUSE_CONSENT`, `FOREIGN_EMPLOYMENT_CONTRACT`, `TAX_RESIDENCY_CERT`
- `extra_checks`: `BIK_APPLICANT`, `BIK_SPOUSE`, `FX_RISK_REVIEW`

## Common mistakes
- Spouse income counts at 50% (bonus share applies to the spouse as well), but ALL spouse installments and card limits count.
- Living costs cover two adults plus children.
- First convert applicant base and bonus income from EUR to PLN at the quoted rate, then apply the counted bonus share, then the 85% haircut.
- Applicant installments and card limits are already in PLN.
- The spouse (if any) earns in PLN; no conversion or haircut for the spouse.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
