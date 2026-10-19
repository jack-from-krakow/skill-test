---
name: single-rev-large-civil-contract
description: "Revolving credit line (overdraft/card limit) for single applicants (not married), requested amount ABOVE 50,000 PLN, applicant working on civil-law contracts (umowa zlecenie / o dzie\u0142o)."
---

# Procedure SINGLE_REV_LARGE_CIVIL_CONTRACT: Revolving credit line above 50,000 PLN for a single applicant, applicant working on civil-law contracts (umowa zlecenie / o dzieło)

## When to use
Use this procedure when the applicant is single (no spouse), the product is a revolving credit line, the requested amount is strictly greater than 50,000 PLN and the applicant is working on civil-law contracts (umowa zlecenie / o dzieło).

## Why the procedure looks like this
Large revolving lines are offered to affluent single clients against a pledge on their savings held at the bank. The pledge is not loan-to-value tested (there is no LTV limit), but the deposit balance is reported as the collateral value. The 300 bps stress reflects the variable rate on revolving products.

## Applicant's employment
Civil-law contracts (umowa zlecenie / umowa o dzieło) can be terminated at any time and give no paid leave or notice period, so only 70% of the applicant's income is recognised and the bank requires 12 months of contract history and a continuity check.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_REV_LARGE_CIVIL_CONTRACT`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 70% x (applicant base income + 50% of applicant bonus income). All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1150 PLN + number of dependent children x 550 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits.
- `dti_limit`: `0.24`
- `stress_test_bps`: `300`
- `collateral_type`: `deposit_pledge`, `collateral_value`: the savings balance from the application, `ltv_limit`: `null`
- `scoring_model`: `REVOLVING_PRO_CC`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `BANK_STATEMENTS_6M`, `DEPOSIT_PLEDGE_AGREEMENT`, `CIVIL_CONTRACTS_12M`
- `extra_checks`: `BIK_APPLICANT`, `AML_ENHANCED`, `INCOME_CONTINUITY`

## Common mistakes
- collateral_value is the applicant's savings balance, not the requested limit.
- ltv_limit is null (deposit pledges are not LTV-tested).
- The 70% haircut applies to the applicant's base income plus the counted bonus, not to the spouse.
- Keep INCOME_STATEMENT and add CIVIL_CONTRACTS_12M.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
