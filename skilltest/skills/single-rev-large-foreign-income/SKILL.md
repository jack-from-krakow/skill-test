---
name: single-rev-large-foreign-income
description: "Revolving credit line (overdraft/card limit) for single applicants (not married), requested amount ABOVE 50,000 PLN, applicant earning in EUR from an employer abroad."
---

# Procedure SINGLE_REV_LARGE_FOREIGN_INCOME: Revolving credit line above 50,000 PLN for a single applicant, applicant earning in EUR from an employer abroad

## When to use
Use this procedure when the applicant is single (no spouse), the product is a revolving credit line, the requested amount is strictly greater than 50,000 PLN and the applicant is earning in EUR from an employer abroad.

## Why the procedure looks like this
Large revolving lines are offered to affluent single clients against a pledge on their savings held at the bank. The pledge is not loan-to-value tested (there is no LTV limit), but the deposit balance is reported as the collateral value. The 300 bps stress reflects the variable rate on revolving products.

## Applicant's employment
The applicant is paid in EUR by an employer abroad while the loan is in PLN. Convert the applicant's EUR amounts to PLN at the rate quoted in the application, then recognise 85% of the result to cover currency risk; an extra 100 bps is added to the stress test.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_REV_LARGE_FOREIGN_INCOME`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = 85% x ((applicant base income + 50% of applicant bonus income, both converted from EUR at the quoted rate)). All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1100 PLN + number of dependent children x 450 PLN.
- `monthly_obligations` = applicant existing installments + 5% of applicant credit-card limits.
- `dti_limit`: `0.26`
- `stress_test_bps`: `400`
- `collateral_type`: `deposit_pledge`, `collateral_value`: the savings balance from the application, `ltv_limit`: `null`
- `scoring_model`: `REVOLVING_PRO_FX`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`, `BANK_STATEMENTS_6M`, `DEPOSIT_PLEDGE_AGREEMENT`, `FOREIGN_EMPLOYMENT_CONTRACT`, `TAX_RESIDENCY_CERT`
- `extra_checks`: `BIK_APPLICANT`, `AML_ENHANCED`, `FX_RISK_REVIEW`

## Common mistakes
- collateral_value is the applicant's savings balance, not the requested limit.
- ltv_limit is null (deposit pledges are not LTV-tested).
- First convert applicant base and bonus income from EUR to PLN at the quoted rate, then apply the counted bonus share, then the 85% haircut.
- Applicant installments and card limits are already in PLN.
- The spouse (if any) earns in PLN; no conversion or haircut for the spouse.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
