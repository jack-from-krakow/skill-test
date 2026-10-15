---
name: married-rev-large-foreign-income
description: "Revolving credit line (overdraft/card limit) for married applicants (spouse in the household), requested amount ABOVE 50,000 PLN, applicant earning in EUR from an employer abroad."
---

# Procedure MARRIED_REV_LARGE_FOREIGN_INCOME: Revolving credit line above 50,000 PLN for a married couple, applicant earning in EUR from an employer abroad

## When to use
Use this procedure when the applicant is married (a spouse is listed in the application), the product is a revolving credit line, the requested amount is strictly greater than 50,000 PLN and the applicant is earning in EUR from an employer abroad.

## Why the procedure looks like this
Large revolving lines for married clients are secured by a pledge on the couple's savings, which requires the spouse's consent. The spouse becomes a guarantor rather than a co-borrower, which the bank reflects by recognising 70% of the spouse's income while counting all of the spouse's obligations.

## Applicant's employment
The applicant is paid in EUR by an employer abroad while the loan is in PLN. Convert the applicant's EUR amounts to PLN at the rate quoted in the application, then recognise 85% of the result to cover currency risk; an extra 100 bps is added to the stress test.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `MARRIED_REV_LARGE_FOREIGN_INCOME`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 85% x ((applicant base income + 50% of applicant bonus income, both converted from EUR at the quoted rate)) + 70% x (spouse base income + 50% of spouse bonus income). All amounts are monthly net PLN.
- `living_costs` = 2 adults x 1200 PLN + number of dependent children x 450 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits + spouse existing installments + 5% of spouse credit-card limits.
- `dti_limit`: `0.31`
- `stress_test_bps`: `400`
- `collateral_type`: `deposit_pledge`, `collateral_value`: the savings balance from the application (joint savings of the couple), `ltv_limit`: `null`
- `scoring_model`: `REVOLVING_PRO_JOINT_FX`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `SPOUSE_INCOME_STATEMENT`, `BANK_STATEMENTS_6M`, `DEPOSIT_PLEDGE_AGREEMENT`, `SPOUSE_CONSENT`, `FOREIGN_EMPLOYMENT_CONTRACT`, `TAX_RESIDENCY_CERT`
- `extra_checks`: `BIK_APPLICANT`, `BIK_SPOUSE`, `AML_ENHANCED`, `FX_RISK_REVIEW`

## Common mistakes
- Spouse income at 70% (after applying the 50% bonus share to the spouse's bonus).
- collateral_value is the couple's savings balance.
- First convert applicant base and bonus income from EUR to PLN at the quoted rate, then apply the counted bonus share, then the 85% haircut.
- Applicant installments and card limits are already in PLN.
- The spouse (if any) earns in PLN; no conversion or haircut for the spouse.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
