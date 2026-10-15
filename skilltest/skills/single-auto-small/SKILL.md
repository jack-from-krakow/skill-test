---
name: single-auto-small
description: "Credit procedure SINGLE_AUTO_SMALL: car loan for single applicants (not married), requested amount UP TO 50,000 PLN (inclusive). Read before calling credit_analysis_engine for such an application."
---

# Procedure SINGLE_AUTO_SMALL: Car loan up to 50,000 PLN for a single applicant

## When to use
Use this procedure when the applicant is single (no spouse), the product is a car loan and the requested amount is at most 50,000 PLN (50,000 itself is small).

## Why the procedure looks like this
Small car loans for single applicants are a high-volume, low-touch product. The bank accepts the full variable income because the exposure is short and small, and it does not register the car as collateral: the cost of a registration pledge would exceed the expected loss. Speed matters more than depth here, so only the applicant's credit bureau (BIK) report is checked.

## How to fill the credit_analysis_engine arguments
- `procedure_code`: `SINGLE_AUTO_SMALL`
- `requested_amount`, `term_months`: copy from the application.
- `monthly_income` = applicant base income + 100% of applicant bonus income. All amounts are monthly net PLN.
- `living_costs` = 1 adult x 1300 PLN + number of dependent children x 600 PLN.
- `monthly_obligations` = applicant existing installments + 3% of applicant credit-card limits.
- `dti_limit`: `0.5`
- `stress_test_bps`: `0`
- `collateral_type`: `none`, `collateral_value`: `0`, `ltv_limit`: `null`
- `scoring_model`: `RETAIL_LITE`
- `required_documents`: `ID_CARD`, `INCOME_STATEMENT`
- `extra_checks`: `BIK_APPLICANT`

## Common mistakes
- Do not add the vehicle as collateral even if its price is given; collateral_type is 'none' and collateral_value is 0.
- No stress test for this product: stress_test_bps is 0.
- Call `credit_analysis_engine` exactly once, with all arguments computed as above. Do not call it again to "double-check".

## After the call
Report the engine's decision to the user in a short summary: decision, DTI after stress, LTV (if any), and the documents the client still has to provide.
