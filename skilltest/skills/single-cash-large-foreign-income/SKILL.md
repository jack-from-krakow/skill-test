---
name: single-cash-large-foreign-income
description: "Unsecured cash loan for single applicants (not married), requested amount ABOVE 50,000 PLN, applicant earning in EUR from an employer abroad."
---

# Procedure SINGLE_CASH_LARGE_FOREIGN_INCOME: Cash loan above 50,000 PLN for a single applicant, applicant earning in EUR from an employer abroad

## When to use
Use this procedure when the applicant is single (no spouse), the product is an unsecured cash loan, the requested amount is strictly greater than 50,000 PLN and the applicant is earning in EUR from an employer abroad.

## Why the procedure looks like this
Large unsecured cash loans are the riskiest retail product: no collateral, long terms and frequent use for debt consolidation. Bonus income counts at 50%, a 200 bps rate shock is applied and the purpose of large disbursements is reviewed by the AML team.

## Applicant's employment
The applicant is paid in EUR by an employer abroad while the loan is in PLN. Convert the applicant's EUR amounts to PLN at the rate quoted in the application, then recognise 85% of the result to cover currency risk; an extra 100 bps is added to the stress test.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_CASH_LARGE_FOREIGN_INCOME`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 85% x ((applicant base income + 50% of applicant bonus income, both converted from EUR at the quoted rate)). All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1350 PLN + number of dependent children x 650 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits.
- `dti_limit`: `0.38`
- `stress_test_bps`: `300`
- `collateral_type`: `none`, `collateral_value`: `0`, `ltv_limit`: `null`
- `scoring_model`: `CASH_PRO_FX`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `BANK_STATEMENTS_3M`, `FOREIGN_EMPLOYMENT_CONTRACT`, `TAX_RESIDENCY_CERT`
- `extra_checks`: `BIK_APPLICANT`, `AML_ENHANCED`, `FX_RISK_REVIEW`

## Common mistakes
- No collateral even for large amounts.
- Card limits count at 5%.
- First convert applicant base and bonus income from EUR to PLN at the quoted rate, then apply the counted bonus share, then the 85% haircut.
- Applicant installments and card limits are already in PLN.
- The spouse (if any) earns in PLN; no conversion or haircut for the spouse.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
