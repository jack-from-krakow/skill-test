---
name: married-rev-large-employee
description: "Revolving credit line (overdraft/card limit) for married applicants (spouse in the household), requested amount ABOVE 50,000 PLN, applicant employed on a standard employment contract."
---

# Procedure MARRIED_REV_LARGE_EMPLOYEE: Revolving credit line above 50,000 PLN for a married couple, applicant employed on a standard employment contract

## When to use
Use this procedure when the applicant is married (a spouse is listed in the application), the product is a revolving credit line, the requested amount is strictly greater than 50,000 PLN and the applicant is employed on a standard employment contract.

## Why the procedure looks like this
Large revolving lines for married clients are secured by a pledge on the couple's savings, which requires the spouse's consent. The spouse becomes a guarantor rather than a co-borrower, which the bank reflects by recognising 70% of the spouse's income while counting all of the spouse's obligations.

## Applicant's employment
The applicant has a standard employment contract (umowa o pracę), so the income statement issued by the employer is sufficient and no income haircut applies.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `MARRIED_REV_LARGE_EMPLOYEE`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = applicant base income + 50% of applicant bonus income + 70% x (spouse base income + 50% of spouse bonus income). All amounts are monthly net PLN.
- `living_costs` = 2 adults x 1200 PLN + number of dependent children x 500 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits + spouse existing installments + 5% of spouse credit-card limits.
- `dti_limit`: `0.31`
- `stress_test_bps`: `300`
- `collateral_type`: `deposit_pledge`, `collateral_value`: the savings balance from the application (joint savings of the couple), `ltv_limit`: `null`
- `scoring_model`: `REVOLVING_PRO_JOINT`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `SPOUSE_INCOME_STATEMENT`, `BANK_STATEMENTS_6M`, `DEPOSIT_PLEDGE_AGREEMENT`, `SPOUSE_CONSENT`
- `extra_checks`: `BIK_APPLICANT`, `BIK_SPOUSE`, `AML_ENHANCED`

## Common mistakes
- Spouse income at 70% (after applying the 50% bonus share to the spouse's bonus).
- collateral_value is the couple's savings balance.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
