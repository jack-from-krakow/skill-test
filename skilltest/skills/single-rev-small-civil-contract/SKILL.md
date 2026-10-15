---
name: single-rev-small-civil-contract
description: "Revolving credit line (overdraft/card limit) for single applicants (not married), requested amount UP TO 50,000 PLN (inclusive), applicant working on civil-law contracts (umowa zlecenie / o dzie\u0142o)."
---

# Procedure SINGLE_REV_SMALL_CIVIL_CONTRACT: Revolving credit line up to 50,000 PLN for a single applicant, applicant working on civil-law contracts (umowa zlecenie / o dzieło)

## When to use
Use this procedure when the applicant is single (no spouse), the product is a revolving credit line, the requested amount is at most 50,000 PLN (50,000 itself is small) and the applicant is working on civil-law contracts (umowa zlecenie / o dzieło).

## Why the procedure looks like this
A small revolving line (overdraft or card limit) is unsecured and repriced every year, so no stress test is applied. The DTI limit is tight because the installment the engine computes for a revolving line is only a proxy for the real utilisation risk.

## Applicant's employment
Civil-law contracts (umowa zlecenie / umowa o dzieło) can be terminated at any time and give no paid leave or notice period, so only 70% of the applicant's income is recognised and the bank requires 12 months of contract history and a continuity check.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_REV_SMALL_CIVIL_CONTRACT`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 70% x (applicant base income + 100% of applicant bonus income). All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1100 PLN + number of dependent children x 550 PLN.
- `monthly_obligations` = applicant existing installments + 3% of applicant credit-card limits.
- `dti_limit`: `0.3`
- `stress_test_bps`: `0`
- `collateral_type`: `none`, `collateral_value`: `0`, `ltv_limit`: `null`
- `scoring_model`: `REVOLVING_LITE_CC`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `CIVIL_CONTRACTS_12M`
- `extra_checks`: `BIK_APPLICANT`, `INCOME_CONTINUITY`

## Common mistakes
- No collateral.
- The 70% haircut applies to the applicant's base income plus the counted bonus, not to the spouse.
- Keep INCOME_STATEMENT and add CIVIL_CONTRACTS_12M.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
