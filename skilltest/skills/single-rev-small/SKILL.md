---
name: single-rev-small
description: "Credit procedure SINGLE_REV_SMALL: revolving credit line (overdraft/card limit) for single applicants (not married), requested amount UP TO 50,000 PLN (inclusive). Read before calling credit_analysis_engine for such an application."
---

# Procedure SINGLE_REV_SMALL: Revolving credit line up to 50,000 PLN for a single applicant

## When to use
Use this procedure when the applicant is single (no spouse), the product is a revolving credit line and the requested amount is at most 50,000 PLN (50,000 itself is small).

## Why the procedure looks like this
A small revolving line (overdraft or card limit) is unsecured and repriced every year, so no stress test is applied. The DTI limit is tight because the installment the engine computes for a revolving line is only a proxy for the real utilisation risk.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_REV_SMALL`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = applicant base income + 100% of applicant bonus income. All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1200 PLN + number of dependent children x 500 PLN.
- `monthly_obligations` = applicant existing installments + 3% of applicant credit-card limits.
- `dti_limit`: `0.35`
- `stress_test_bps`: `0`
- `collateral_type`: `none`, `collateral_value`: `0`, `ltv_limit`: `null`
- `scoring_model`: `REVOLVING_LITE`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`
- `extra_checks`: `BIK_APPLICANT`

## Common mistakes
- No collateral and no stress test.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
