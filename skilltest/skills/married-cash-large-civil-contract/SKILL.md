---
name: married-cash-large-civil-contract
description: "Unsecured cash loan for married applicants (spouse in the household), requested amount ABOVE 50,000 PLN, applicant working on civil-law contracts (umowa zlecenie / o dzie\u0142o)."
---

# Procedure MARRIED_CASH_LARGE_CIVIL_CONTRACT: Cash loan above 50,000 PLN for a married couple, applicant working on civil-law contracts (umowa zlecenie / o dzieło)

## When to use
Use this procedure when the applicant is married (a spouse is listed in the application), the product is an unsecured cash loan, the requested amount is strictly greater than 50,000 PLN and the applicant is working on civil-law contracts (umowa zlecenie / o dzieło).

## Why the procedure looks like this
Large cash loans for married couples are joint loans with both spouses as co-borrowers: both incomes count in full (bonuses at 50%), both credit histories are checked and the AML review of the loan purpose applies.

## Applicant's employment
Civil-law contracts (umowa zlecenie / umowa o dzieło) can be terminated at any time and give no paid leave or notice period, so only 70% of the applicant's income is recognised and the bank requires 12 months of contract history and a continuity check.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `MARRIED_CASH_LARGE_CIVIL_CONTRACT`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 70% x (applicant base income + 50% of applicant bonus income) + 100% x (spouse base income + 50% of spouse bonus income). All amounts are monthly net PLN.
- `living_costs` = 2 adults x 1200 PLN + number of dependent children x 600 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits + spouse existing installments + 5% of spouse credit-card limits.
- `dti_limit`: `0.39`
- `stress_test_bps`: `200`
- `collateral_type`: `none`, `collateral_value`: `0`, `ltv_limit`: `null`
- `scoring_model`: `CASH_PRO_JOINT_CC`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `SPOUSE_INCOME_STATEMENT`, `BANK_STATEMENTS_3M`, `CIVIL_CONTRACTS_12M`
- `extra_checks`: `BIK_APPLICANT`, `BIK_SPOUSE`, `AML_ENHANCED`, `INCOME_CONTINUITY`

## Common mistakes
- Both spouses are co-borrowers: spouse income at 100%.
- The 70% haircut applies to the applicant's base income plus the counted bonus, not to the spouse.
- Keep INCOME_STATEMENT and add CIVIL_CONTRACTS_12M.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
