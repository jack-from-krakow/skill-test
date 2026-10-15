"""The function the agent calls: a deterministic credit analysis engine.

The tool is identical in both variants. Every call is recorded in
``CALL_LOG`` so the benchmark can verify that it was called exactly once and
with the right arguments.
"""

from __future__ import annotations

import json
import time
from typing import Literal

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from .procedures import ALL_CHECKS, ALL_DOCUMENTS, ALL_SCORING_MODELS, BY_CODE

ProcedureCode = Literal[tuple(sorted(BY_CODE))]  # type: ignore[valid-type]
Document = Literal[tuple(ALL_DOCUMENTS)]  # type: ignore[valid-type]
Check = Literal[tuple(ALL_CHECKS)]  # type: ignore[valid-type]
ScoringModel = Literal[tuple(ALL_SCORING_MODELS)]  # type: ignore[valid-type]

BASE_RATE = {"AUTO": 0.09, "HOME": 0.07, "REV": 0.14}

CALL_LOG: list[dict] = []

# The tool's logic does not matter for the benchmark; it only has to take a
# realistic minimum time so wall-clock numbers include tool execution.
MIN_TOOL_SECONDS = 0.020


class EngineArgs(BaseModel):
    procedure_code: ProcedureCode = Field(description="Code of the credit procedure that applies to this application.")
    requested_amount: float = Field(description="Requested loan amount in PLN.")
    term_months: int = Field(description="Loan term in months.")
    monthly_income: float = Field(description="Monthly net income recognised by the procedure, PLN.")
    living_costs: float = Field(description="Monthly household living costs per the procedure, PLN.")
    monthly_obligations: float = Field(description="Existing monthly obligations recognised by the procedure, PLN.")
    dti_limit: float = Field(description="Maximum debt-to-income ratio, e.g. 0.45.")
    stress_test_bps: int = Field(description="Interest-rate shock in basis points added before computing the installment.")
    collateral_type: Literal["none", "vehicle", "property", "deposit_pledge"]
    collateral_value: float = Field(description="Value of the collateral in PLN, 0 when there is none.")
    ltv_limit: float | None = Field(default=None, description="Maximum loan-to-value ratio, or null when not applicable.")
    scoring_model: ScoringModel
    required_documents: list[Document]
    extra_checks: list[Check]


def _installment(amount: float, annual_rate: float, months: int) -> float:
    r = annual_rate / 12
    return amount * r / (1 - (1 + r) ** -months)


def run_engine(args: EngineArgs) -> dict:
    product = args.procedure_code.split("_")[1]
    rate = BASE_RATE[product] + args.stress_test_bps / 10_000
    installment = _installment(args.requested_amount, rate, args.term_months)
    dti = (args.monthly_obligations + installment) / args.monthly_income if args.monthly_income > 0 else 99.0
    buffer = args.monthly_income - args.living_costs - args.monthly_obligations - installment
    ltv = args.requested_amount / args.collateral_value if args.collateral_value > 0 and args.ltv_limit else None

    reasons = []
    if dti > args.dti_limit:
        reasons.append(f"DTI {dti:.3f} above limit {args.dti_limit}")
    if buffer < 0:
        reasons.append(f"negative monthly buffer {buffer:.0f} PLN")
    if ltv is not None and ltv > args.ltv_limit:
        reasons.append(f"LTV {ltv:.3f} above limit {args.ltv_limit}")
    if not reasons:
        decision = "APPROVE"
    elif len(reasons) == 1 and dti <= args.dti_limit * 1.1 and buffer >= 0:
        decision = "REFER"
    else:
        decision = "DECLINE"

    return {
        "decision": decision,
        "stressed_rate": round(rate, 4),
        "installment": round(installment, 2),
        "dti_after_stress": round(dti, 4),
        "monthly_buffer": round(buffer, 2),
        "ltv": None if ltv is None else round(ltv, 4),
        "reasons": reasons,
        "documents_to_collect": args.required_documents,
        "checks_ordered": args.extra_checks,
    }


@tool("credit_analysis_engine", args_schema=EngineArgs)
def credit_analysis_engine(**kwargs) -> str:
    """Run the bank's credit analysis engine for one loan application.

    Computes the stressed installment, debt-to-income, monthly buffer and LTV,
    and returns a decision (APPROVE / REFER / DECLINE). All inputs must be
    prepared according to the credit procedure that applies to the application.
    """
    t0 = time.perf_counter()
    args = EngineArgs(**kwargs)
    CALL_LOG.append(args.model_dump())
    result = json.dumps(run_engine(args))
    remaining = MIN_TOOL_SECONDS - (time.perf_counter() - t0)
    if remaining > 0:
        time.sleep(remaining)
    return result
