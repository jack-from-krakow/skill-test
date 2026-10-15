---
name: single-rev-small-employee
description: "Revolving credit line (overdraft/card limit) for single applicants (not married), requested amount UP TO 50,000 PLN (inclusive), applicant employed on a standard employment contract."
---

# Procedure SINGLE_REV_SMALL_EMPLOYEE: Revolving credit line up to 50,000 PLN for a single applicant, applicant employed on a standard employment contract

## When to use
Use this procedure when the applicant is single (no spouse), the product is a revolving credit line, the requested amount is at most 50,000 PLN (50,000 itself is small) and the applicant is employed on a standard employment contract.

## Why the procedure looks like this
A small revolving line (overdraft or card limit) is unsecured and repriced every year, so no stress test is applied. The DTI limit is tight because the installment the engine computes for a revolving line is only a proxy for the real utilisation risk.

## Applicant's employment
The applicant has a standard employment contract (umowa o pracę), so the income statement issued by the employer is sufficient and no income haircut applies.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_REV_SMALL_EMPLOYEE`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = applicant base income + 100% of applicant bonus income. All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1100 PLN + number of dependent children x 450 PLN.
- `monthly_obligations` = applicant existing installments + 3% of applicant credit-card limits.
- `dti_limit`: `0.34`
- `stress_test_bps`: `0`
- `collateral_type`: `none`, `collateral_value`: `0`, `ltv_limit`: `null`
- `scoring_model`: `REVOLVING_LITE`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`
- `extra_checks`: `BIK_APPLICANT`

## Common mistakes
- No collateral.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
