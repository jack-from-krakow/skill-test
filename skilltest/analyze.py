"""Aggregate runs.jsonl into summary.csv and REPORT.md.

    python -m skilltest.analyze results/<run-dir>
"""

from __future__ import annotations

import csv
import json
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

METRICS = [
    ("fully_correct", "Poprawne argumenty (wszystkie pola)", "pct"),
    ("procedure_correct", "Poprawna procedura", "pct"),
    ("engine_called_once", "Tool wywołany dokładnie 1 raz", "pct"),
    ("fields_ok", "Śr. poprawnych pól (z 14)", "f2"),
    ("llm_calls", "Wywołania modelu / zadanie", "f2"),
    ("input_total", "Tokeny IN razem", "int"),
    ("input_uncached", "  w tym bez cache", "int"),
    ("cache_write", "  w tym zapis do cache", "int"),
    ("cache_read", "  w tym odczyt z cache", "int"),
    ("output", "Tokeny OUT", "int"),
    ("wall_s", "Czas zadania [s]", "f2"),
    ("llm_latency_s", "Czas samego modelu [s]", "f2"),
    ("cost_usd", "Koszt / zadanie [USD]", "usd"),
]


def load(run_dir: Path) -> tuple[dict, list[dict]]:
    meta = json.loads((run_dir / "meta.json").read_text())
    rows = [json.loads(l) for l in (run_dir / "runs.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    return meta, rows


def fmt(v: float, kind: str) -> str:
    if kind == "pct":
        return f"{v * 100:.0f}%"
    if kind == "int":
        return f"{v:,.0f}".replace(",", " ")
    if kind == "usd":
        return f"{v:.5f}"
    return f"{v:.2f}"


def mean(rows: list[dict], key: str) -> float:
    vals = [float(r[key]) for r in rows]
    return st.mean(vals) if vals else 0.0


def sd(rows: list[dict], key: str) -> float:
    vals = [float(r[key]) for r in rows]
    return st.stdev(vals) if len(vals) > 1 else 0.0


def main() -> None:
    run_dir = Path(sys.argv[1])
    meta, rows = load(run_dir)
    by_v: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_v[r["variant"]].append(r)
    variants = sorted(by_v)

    with (run_dir / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["variant", "metric", "mean", "stdev", "n"])
        for v in variants:
            for key, _, _ in METRICS:
                w.writerow([v, key, round(mean(by_v[v], key), 6), round(sd(by_v[v], key), 6), len(by_v[v])])

    out: list[str] = []
    add = out.append
    add(f"# Wyniki: {run_dir.name}")
    add("")
    if meta.get("dry_run"):
        add("> **UWAGA: przebieg na sucho (scripted fake model).** Tokeny to szacunki (znaki/4), czasy i trafność nic nie mówią o modelu. Służy tylko do sprawdzenia, że cały pipeline działa.")
        add("")
    add(f"Model: `{meta['model']}`, effort: `{meta.get('effort') or 'domyślny'}`, powtórzeń: {meta['runs']}, przypadków na powtórzenie: {meta.get('cases_per_run', len(meta.get('cases', [])))} (losowane, seed {meta.get('seed', '–')}), start: {meta['started_utc']}.")
    add("")
    add("## Średnie na jedno zadanie (jedna aplikacja kredytowa)")
    add("")
    others = [v for v in variants if v != "A"] if "A" in by_v else []
    add("| Metryka | " + " | ".join(f"Wariant {v} (n={len(by_v[v])})" for v in variants) + "".join(f" | {v} / A" for v in others) + " |")
    add("|---|" + "---|" * (len(variants) + len(others)))
    for key, label, kind in METRICS:
        cells = []
        for v in variants:
            m, s = mean(by_v[v], key), sd(by_v[v], key)
            cells.append(fmt(m, kind) + (f" ± {fmt(s, kind)}" if kind not in ("pct",) and s else ""))
        for v in others:
            a, b = mean(by_v["A"], key), mean(by_v[v], key)
            cells.append("" if kind == "pct" else (f"{b / a:.2f}×" if a else "–"))
        add(f"| {label} | " + " | ".join(cells) + " |")
    add("")
    add("Warianty: A = wszystkie procedury w system prompcie; B = deepagents + skille; C = B-min (skille + tylko read_file, bez harnessu deepagents).")
    add("")

    add("## Według powtórzenia (wpływ cache)")
    add("")
    add("| Wariant | Powt. | Tokeny IN | odczyt z cache | zapis do cache | Tokeny OUT | Czas [s] | Koszt [USD] | Poprawne |")
    add("|---|---|---|---|---|---|---|---|---|")
    for v in variants:
        reps = sorted({r["rep"] for r in by_v[v]})
        for rep in reps:
            rr = [r for r in by_v[v] if r["rep"] == rep]
            add(
                f"| {v} | {rep} | {fmt(mean(rr, 'input_total'), 'int')} | {fmt(mean(rr, 'cache_read'), 'int')} | "
                f"{fmt(mean(rr, 'cache_write'), 'int')} | {fmt(mean(rr, 'output'), 'int')} | {mean(rr, 'wall_s'):.2f} | "
                f"{mean(rr, 'cost_usd'):.5f} | {fmt(mean(rr, 'fully_correct'), 'pct')} |"
            )
    add("")

    add("## Trafność według przypadku")
    add("")
    add("| Przypadek | Procedura | " + " | ".join(f"{v}: poprawne / wywołań toola" for v in variants) + " |")
    add("|---|---|" + "---|" * len(variants))
    cases = sorted({(r["case_id"], r["procedure"]) for r in rows})
    for cid, proc in cases:
        cells = []
        for v in variants:
            rr = [r for r in by_v[v] if r["case_id"] == cid]
            ok = sum(r["fully_correct"] for r in rr)
            calls = "/".join(str(r["engine_calls"]) for r in sorted(rr, key=lambda r: r["rep"]))
            cells.append(f"{ok}/{len(rr)} (tool: {calls})")
        add(f"| {cid} | {proc} | " + " | ".join(cells) + " |")
    add("")

    add("## Trafność według typu zatrudnienia i produktu")
    add("")
    groups = sorted({(dim, r["procedure"].lower().split("_", 3)[i]) for r in rows for dim, i in (("zatrudnienie", 3), ("produkt", 1)) if r["procedure"].count("_") >= 3})
    if groups:
        add("| Wymiar | Wartość | " + " | ".join(f"{v}: poprawne" for v in variants) + " |")
        add("|---|---|" + "---|" * len(variants))
        for dim, val in groups:
            i = 3 if dim == "zatrudnienie" else 1
            cells = []
            for v in variants:
                rr = [r for r in by_v[v] if r["procedure"].lower().split("_", 3)[i] == val]
                cells.append(f"{sum(r['fully_correct'] for r in rr)}/{len(rr)}")
            add(f"| {dim} | {val} | " + " | ".join(cells) + " |")
        add("")

    add("## Najczęstsze błędne pola")
    add("")
    for v in variants:
        c = Counter(f for r in by_v[v] for f in r["wrong_fields"])
        add(f"- **{v}**: " + (", ".join(f"`{k}` ×{n}" for k, n in c.most_common()) or "brak"))
    add("")

    for v in [v for v in variants if v in ("B", "C")]:
        b = by_v[v]
        read_ok = sum(1 for r in b if r.get("read_expected_skill"))
        n_reads = [len(r.get("skill_reads") or []) for r in b]
        add(f"## Zachowanie skilli w wariancie {v}")
        add("")
        add(f"- Przeczytano właściwy skill: {read_ok}/{len(b)} zadań")
        add(f"- Średnio odczytów `read_file` na zadanie: {st.mean(n_reads):.2f} (max {max(n_reads)})")
        seqs = Counter(" → ".join(r["tool_sequence"]) for r in b)
        add("- Sekwencje narzędzi:")
        for s_, n in seqs.most_common(8):
            add(f"  - `{s_ or '(brak)'}` ×{n}")
        add("")

    errs = [r for r in rows if r.get("error")]
    if errs:
        add("## Błędy wykonania")
        add("")
        for r in errs:
            add(f"- {r['variant']} {r['case_id']} rep {r['rep']}: {r['error'][:300]}")
        add("")

    (run_dir / "REPORT.md").write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
