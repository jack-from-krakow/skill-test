---
name: married-cash-small-civil-contract
description: "Unsecured cash loan for married applicants (spouse in the household), requested amount UP TO 50,000 PLN (inclusive), applicant working on civil-law contracts (umowa zlecenie / o dzie\u0142o)."
---

# Procedure MARRIED_CASH_SMALL_CIVIL_CONTRACT: Cash loan up to 50,000 PLN for a married couple, applicant working on civil-law contracts (umowa zlecenie / o dzieło)

## When to use
Use this procedure when the applicant is married (a spouse is listed in the application), the product is an unsecured cash loan, the requested amount is at most 50,000 PLN (50,000 itself is small) and the applicant is working on civil-law contracts (umowa zlecenie / o dzieło).

## Why the procedure looks like this
For a small cash loan the spouse only signs a consent; the bank recognises half of the spouse's income and all of the spouse's obligations, because under Polish family law the debt burdens the joint household.

## Applicant's employment
Civil-law contracts (umowa zlecenie / umowa o dzieło) can be terminated at any time and give no paid leave or notice period, so only 70% of the applicant's income is recognised and the bank requires 12 months of contract history and a continuity check.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `MARRIED_CASH_SMALL_CIVIL_CONTRACT`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 70% x (applicant base income + 100% of applicant bonus income) + 50% x (spouse base income + 100% of spouse bonus income). All amounts are monthly net PLN.
- `living_costs` = 2 adults x 1000 PLN + number of dependent children x 650 PLN.
- `monthly_obligations` = applicant existing installments + 3% of applicant credit-card limits + spouse existing installments + 3% of spouse credit-card limits.
- `dti_limit`: `0.47`
- `stress_test_bps`: `0`
- `collateral_type`: `none`, `collateral_value`: `0`, `ltv_limit`: `null`
- `scoring_model`: `CASH_LITE_JOINT_CC`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `SPOUSE_CONSENT`, `CIVIL_CONTRACTS_12M`
- `extra_checks`: `BIK_APPLICANT`, `BIK_SPOUSE`, `INCOME_CONTINUITY`

## Common mistakes
- Spouse income at 50%, spouse obligations at 100%.
- The 70% haircut applies to the applicant's base income plus the counted bonus, not to the spouse.
- Keep INCOME_STATEMENT and add CIVIL_CONTRACTS_12M.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
