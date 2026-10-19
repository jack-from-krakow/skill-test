---
name: single-cash-large-employee
description: "Unsecured cash loan for single applicants (not married), requested amount ABOVE 50,000 PLN, applicant employed on a standard employment contract."
---

# Procedure SINGLE_CASH_LARGE_EMPLOYEE: Cash loan above 50,000 PLN for a single applicant, applicant employed on a standard employment contract

## When to use
Use this procedure when the applicant is single (no spouse), the product is an unsecured cash loan, the requested amount is strictly greater than 50,000 PLN and the applicant is employed on a standard employment contract.

## Why the procedure looks like this
Large unsecured cash loans are the riskiest retail product: no collateral, long terms and frequent use for debt consolidation. Bonus income counts at 50%, a 200 bps rate shock is applied and the purpose of large disbursements is reviewed by the AML team.

## Applicant's employment
The applicant has a standard employment contract (umowa o pracę), so the income statement issued by the employer is sufficient and no income haircut applies.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_CASH_LARGE_EMPLOYEE`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = applicant base income + 50% of applicant bonus income. All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1350 PLN + number of dependent children x 600 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits.
- `dti_limit`: `0.4`
- `stress_test_bps`: `200`
- `collateral_type`: `none`, `collateral_value`: `0`, `ltv_limit`: `null`
- `scoring_model`: `CASH_PRO`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `BANK_STATEMENTS_3M`
- `extra_checks`: `BIK_APPLICANT`, `AML_ENHANCED`

## Common mistakes
- No collateral even for large amounts.
- Card limits count at 5%.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
