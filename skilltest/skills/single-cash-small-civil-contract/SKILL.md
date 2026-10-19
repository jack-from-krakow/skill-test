---
name: single-cash-small-civil-contract
description: "Unsecured cash loan for single applicants (not married), requested amount UP TO 50,000 PLN (inclusive), applicant working on civil-law contracts (umowa zlecenie / o dzie\u0142o)."
---

# Procedure SINGLE_CASH_SMALL_CIVIL_CONTRACT: Cash loan up to 50,000 PLN for a single applicant, applicant working on civil-law contracts (umowa zlecenie / o dzieło)

## When to use
Use this procedure when the applicant is single (no spouse), the product is an unsecured cash loan, the requested amount is at most 50,000 PLN (50,000 itself is small) and the applicant is working on civil-law contracts (umowa zlecenie / o dzieło).

## Why the procedure looks like this
Small unsecured cash loans are sold through the mobile app with an automated decision. The exposure is small and short, so the full bonus counts and no stress test is applied, but the DTI limit is lower than for car loans because there is no asset behind the loan.

## Applicant's employment
Civil-law contracts (umowa zlecenie / umowa o dzieło) can be terminated at any time and give no paid leave or notice period, so only 70% of the applicant's income is recognised and the bank requires 12 months of contract history and a continuity check.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_CASH_SMALL_CIVIL_CONTRACT`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 70% x (applicant base income + 100% of applicant bonus income). All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1200 PLN + number of dependent children x 650 PLN.
- `monthly_obligations` = applicant existing installments + 3% of applicant credit-card limits.
- `dti_limit`: `0.41`
- `stress_test_bps`: `0`
- `collateral_type`: `none`, `collateral_value`: `0`, `ltv_limit`: `null`
- `scoring_model`: `CASH_LITE_CC`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `CIVIL_CONTRACTS_12M`
- `extra_checks`: `BIK_APPLICANT`, `INCOME_CONTINUITY`

## Common mistakes
- Cash loans are never secured: collateral_type 'none', collateral_value 0.
- The 70% haircut applies to the applicant's base income plus the counted bonus, not to the spouse.
- Keep INCOME_STATEMENT and add CIVIL_CONTRACTS_12M.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
