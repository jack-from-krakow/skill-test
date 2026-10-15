---
name: single-cash-small-employee
description: "Unsecured cash loan for single applicants (not married), requested amount UP TO 50,000 PLN (inclusive), applicant employed on a standard employment contract."
---

# Procedure SINGLE_CASH_SMALL_EMPLOYEE: Cash loan up to 50,000 PLN for a single applicant, applicant employed on a standard employment contract

## When to use
Use this procedure when the applicant is single (no spouse), the product is an unsecured cash loan, the requested amount is at most 50,000 PLN (50,000 itself is small) and the applicant is employed on a standard employment contract.

## Why the procedure looks like this
Small unsecured cash loans are sold through the mobile app with an automated decision. The exposure is small and short, so the full bonus counts and no stress test is applied, but the DTI limit is lower than for car loans because there is no asset behind the loan.

## Applicant's employment
The applicant has a standard employment contract (umowa o pracę), so the income statement issued by the employer is sufficient and no income haircut applies.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_CASH_SMALL_EMPLOYEE`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = applicant base income + 100% of applicant bonus income. All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1250 PLN + number of dependent children x 550 PLN.
- `monthly_obligations` = applicant existing installments + 3% of applicant credit-card limits.
- `dti_limit`: `0.46`
- `stress_test_bps`: `0`
- `collateral_type`: `none`, `collateral_value`: `0`, `ltv_limit`: `null`
- `scoring_model`: `CASH_LITE`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`
- `extra_checks`: `BIK_APPLICANT`

## Common mistakes
- Cash loans are never secured: collateral_type 'none', collateral_value 0.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
