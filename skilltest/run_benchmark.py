"""Run the A/B benchmark.

    python -m skilltest.run_benchmark --runs 3 --cases-per-run 15   # real run, needs ANTHROPIC_API_KEY
    python -m skilltest.run_benchmark --runs 1 --dry-run            # offline plumbing check, scripted model
    python -m skilltest.run_benchmark --model ollama:qwen3.8:27b    # local model

Every repetition draws its own random sample of procedures (seed = --seed + rep)
and generates one application per procedure; variants A and B get exactly the
same applications. The cases of every repetition are saved to cases_rep<N>.json.

Every agent run is appended to <out>/runs.jsonl as soon as it finishes, so an
interrupted benchmark keeps everything measured so far.
"""

from __future__ import annotations

import argparse
import json
import os
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from . import engine
from .agents import BUILDERS, DEFAULT_MODEL, make_model
from .cases import sample_cases
from .metrics import UsageRecorder, grade
from .procedures import BY_CODE

ROOT = Path(__file__).resolve().parent.parent


def run_one(variant: str, case: dict, model, recursion_limit: int = 30) -> dict:
    agent = BUILDERS[variant](model)
    engine.CALL_LOG.clear()
    rec = UsageRecorder()
    t0 = time.perf_counter()
    error = None
    messages = []
    try:
        out = agent.invoke(
            {"messages": [HumanMessage(case["prompt"])]},
            config={"callbacks": [rec], "recursion_limit": recursion_limit},
        )
        messages = out["messages"]
    except Exception as exc:  # recorded, the benchmark goes on
        error = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()
    wall = time.perf_counter() - t0

    tool_seq = [tc["name"] for m in messages if isinstance(m, AIMessage) for tc in (m.tool_calls or [])]
    skill_reads = [
        tc["args"].get("file_path")
        for m in messages
        if isinstance(m, AIMessage)
        for tc in (m.tool_calls or [])
        if tc["name"] == "read_file"
    ]
    engine_errors = [
        str(m.content)[:300]
        for m in messages
        if isinstance(m, ToolMessage) and m.name == "credit_analysis_engine" and getattr(m, "status", "") == "error"
    ]
    final = next((m for m in reversed(messages) if isinstance(m, AIMessage) and not m.tool_calls), None)
    final_text = ""
    if final is not None:
        final_text = final.content if isinstance(final.content, str) else " ".join(
            b.get("text", "") for b in final.content if isinstance(b, dict)
        )

    calls = list(engine.CALL_LOG)
    first_call = calls[0] if calls else None
    g = grade(first_call, case["expected"])
    expected_skill = f"/skills/{BY_CODE[case['procedure_code']].skill_name}/SKILL.md"

    return {
        "variant": variant,
        "case_id": case["id"],
        "procedure": case["procedure_code"],
        "wall_s": round(wall, 3),
        **rec.totals(),
        "calls": rec.calls,
        "tool_sequence": tool_seq,
        "engine_calls": len(calls),
        "engine_called_once": len(calls) == 1,
        "engine_errors": engine_errors,
        "procedure_correct": bool(first_call and first_call.get("procedure_code") == case["procedure_code"]),
        **g,
        "engine_args": first_call,
        "skill_reads": skill_reads,
        "read_expected_skill": expected_skill in skill_reads if variant == "B" else None,
        "final_text": final_text[:2000],
        "error": error,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--variants", nargs="+", default=["A", "B"], choices=["A", "B"])
    ap.add_argument("--cases-per-run", type=int, default=15, help="random procedures per repetition (max 80)")
    ap.add_argument("--seed", type=int, default=None, help="base seed (default: random, saved in meta.json)")
    ap.add_argument("--model", default=DEFAULT_MODEL, help="claude-haiku-5-5 | ollama:<model> | openai:<model>")
    ap.add_argument("--num-ctx", type=int, default=131072, help="context window for ollama models")
    ap.add_argument("--effort", default=None, help="output_config.effort (default: model default)")
    ap.add_argument("--dry-run", action="store_true", help="scripted offline model, no API calls")
    ap.add_argument("--out", default=None, help="output dir (default results/<timestamp>)")
    args = ap.parse_args()

    try:
        from dotenv import load_dotenv

        load_dotenv(ROOT / ".env")
    except ImportError:
        pass
    anthropic = ":" not in args.model or args.model.startswith("anthropic:")
    if not args.dry_run and anthropic and not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
        raise SystemExit("ANTHROPIC_API_KEY is not set (put it in the environment or in .env). Use --dry-run for an offline check.")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(args.out) if args.out else ROOT / "results" / (("dryrun-" if args.dry_run else "") + stamp)
    out_dir.mkdir(parents=True, exist_ok=True)
    seed = args.seed if args.seed is not None else int.from_bytes(os.urandom(3), "big")
    meta = {
        "started_utc": stamp,
        "model": "scripted-fake" if args.dry_run else args.model,
        "effort": args.effort,
        "runs": args.runs,
        "variants": args.variants,
        "cases_per_run": args.cases_per_run,
        "seed": seed,
        "dry_run": args.dry_run,
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    runs_path = out_dir / "runs.jsonl"

    total = args.runs * args.cases_per_run * len(args.variants)
    done = 0
    for rep in range(1, args.runs + 1):
        cases = sample_cases(args.cases_per_run, seed + rep)
        (out_dir / f"cases_rep{rep}.json").write_text(json.dumps(cases, indent=1, ensure_ascii=False), encoding="utf-8")
        for case in cases:
            for variant in args.variants:
                if args.dry_run:
                    from .fake_model import ScriptedModel

                    skill = f"/skills/{BY_CODE[case['procedure_code']].skill_name}/SKILL.md"
                    model = ScriptedModel(case=case, skill_path=skill if variant == "B" else None)
                else:
                    model = make_model(args.model, args.effort, args.num_ctx)
                r = run_one(variant, case, model)
                r["rep"] = rep
                with runs_path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
                done += 1
                print(
                    f"[{done}/{total}] rep={rep} {variant} {case['id']} {case['procedure_code']:<36} "
                    f"ok={r['fully_correct']!s:<5} engine_calls={r['engine_calls']} llm_calls={r['llm_calls']} "
                    f"in={r['input_total']} (cache_read={r['cache_read']}) out={r['output']} {r['wall_s']:.1f}s"
                    + (f" ERROR {r['error']}" if r["error"] else ""),
                    flush=True,
                )
    meta["finished_utc"] = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    print(f"\nraw results: {runs_path}\nnext: python -m skilltest.analyze {out_dir}")


if __name__ == "__main__":
    main()
