"""Constraint-level behavioral diagnosis.

Given the OBSERVED marked set of a failing oracle (free by-product of the
method-A phase table) and the instance's machine-readable constraints,
produce a semantic diff instead of raw counterexamples:

  1. exact single-edit matching: does the oracle behave EXACTLY like the
     correct predicate with one constraint dropped / one polarity flipped /
     a non-surjective decode (11 treated as a 4th color) / an off-by-one
     bound?  (Validated on real failures: ~22% of 3sat MARK_MISMATCHes
     match a single edit.)
  2. per-constraint respect scorecard: for each constraint j, the fraction
     of *decisive* inputs (violating only j) handled correctly -- always
     computable, localizes the broken constraint.

Both are computed modulo the global phase flip (both orientations tried).
The rendered text feeds the repair prompts.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from qencodebench.core.circuits import decode_color
from qencodebench.core.task import TaskInstance
from qencodebench.generators.f1_sat import clause_satisfied
from qencodebench.generators.f5_latin_square import constraints_of
from qencodebench.generators.f6_string_match import matches_at

MAX_SCORECARD_LINES = 8


@dataclass
class Diagnosis:
    exact: str | None = None            # single-edit exact match, if any
    scorecard: list = field(default_factory=list)  # (name, respect, n)
    overall_sat_marked: float | None = None
    text: str = ""


# ---------------------------------------------------------------------------
# per-family constraint decomposition:  (aggregator, [(name, pred(x))])
# ---------------------------------------------------------------------------

def constraint_predicates(inst: TaskInstance):
    spec = inst.formal_spec
    fam = inst.family
    if fam == "3sat":
        def mk(c):
            return lambda x, c=c: clause_satisfied(c, x)
        names = [f"clause {j+1}" for j in range(len(spec["clauses"]))]
        return "and", list(zip(names, map(mk, spec["clauses"])))
    if fam == "sat_card":
        def mkc(c):
            return lambda x, c=c: clause_satisfied(c, x)
        preds = [(f"clause {j+1}", mkc(c))
                 for j, c in enumerate(spec["clauses"])]
        cmp_, k = spec["cmp"], spec["k"]
        cmp_fn = {"==": lambda a, b: a == b, "<=": lambda a, b: a <= b,
                  ">=": lambda a, b: a >= b}[cmp_]
        preds.append((f"popcount {cmp_} {k}",
                      lambda x: cmp_fn(bin(x).count("1"), k)))
        return "and", preds
    if fam == "coloring":
        def col(x, v):
            return decode_color((x >> (2 * v)) & 0b11)
        preds = [(f"edge ({a},{b}) differs",
                  lambda x, a=a, b=b: col(x, a) != col(x, b))
                 for a, b in spec["edges"]]
        return "and", preds
    if fam == "vertex_cover":
        preds = [(f"edge ({a},{b}) covered",
                  lambda x, a=a, b=b: bool((x >> a) & 1 or (x >> b) & 1))
                 for a, b in spec["edges"]]
        k = spec["k"]
        preds.append((f"cover size <= {k}",
                      lambda x, k=k: bin(x).count("1") <= k))
        return "and", preds
    if fam == "subset_sum":
        vals, t = spec["values"], spec["target"]

        def sums(x):
            return sum(v for i, v in enumerate(vals) if (x >> i) & 1)
        return "and", [(f"sum == {t}", lambda x: sums(x) == t)]
    if fam == "latin_square":
        free = [tuple(c) for c in spec["free_cells"]]

        def cell(x, j):
            return decode_color((x >> (2 * j)) & 0b11)
        preds = []
        for con in constraints_of(spec):
            if con[0] == "pair":
                _, i, j = con
                preds.append((f"cells {free[i]} != {free[j]}",
                              lambda x, i=i, j=j: cell(x, i) != cell(x, j)))
            else:
                _, i, v = con
                preds.append((f"cell {free[i]} != given {v}",
                              lambda x, i=i, v=v: cell(x, i) != v))
        return "and", preds
    if fam == "string_match":
        n, p = spec["n_text"], spec["pattern"]
        if spec["anchored"]:
            return "and", [("anchored match",
                            lambda x: matches_at(x, p, 0))]
        offs = range(n - len(p) + 1)
        return "or", [(f"match at offset {o}",
                       lambda x, o=o: matches_at(x, p, o)) for o in offs]
    raise ValueError(fam)


# ---------------------------------------------------------------------------
# single-edit hypothesis library
# ---------------------------------------------------------------------------

def _sat_set(preds, agg, dim) -> frozenset:
    if agg == "and":
        return frozenset(x for x in range(dim)
                         if all(p(x) for _, p in preds))
    return frozenset(x for x in range(dim) if any(p(x) for _, p in preds))


def edit_hypotheses(inst: TaskInstance) -> list[tuple[str, frozenset]]:
    """(description, predicted marked set) for plausible single edits."""
    spec = inst.formal_spec
    fam = inst.family
    dim = 1 << inst.n_problem_qubits
    agg, preds = constraint_predicates(inst)
    out: list[tuple[str, frozenset]] = []

    def drop(j, label):
        kept = preds[:j] + preds[j + 1:]
        out.append((f"{label} MISSING", _sat_set(kept, agg, dim)))

    for j, (name, _) in enumerate(preds):
        if len(preds) > 1:
            drop(j, f"constraint '{name}'")

    if fam == "3sat":
        clauses = spec["clauses"]
        for j, c in enumerate(clauses):
            flipped = [list(map(list, cc)) for cc in clauses]
            flipped[j] = [[v, 1 - pos] for v, pos in flipped[j]]
            out.append((f"clause {j+1} with ALL polarities flipped",
                        frozenset(x for x in range(dim) if all(
                            clause_satisfied(cc, x) for cc in flipped))))
            for k in range(len(c)):
                f2 = [list(map(list, cc)) for cc in clauses]
                f2[j][k][1] ^= 1
                out.append((f"literal {k+1} of clause {j+1} polarity "
                            "flipped",
                            frozenset(x for x in range(dim) if all(
                                clause_satisfied(cc, x) for cc in f2))))
    if fam == "sat_card":
        clauses, k, cmp_ = spec["clauses"], spec["k"], spec["cmp"]
        cmp_fns = {"==": lambda a, b: a == b, "<=": lambda a, b: a <= b,
                   ">=": lambda a, b: a >= b}

        def sc_set(kk, cc):
            fn = cmp_fns[cc]
            return frozenset(
                x for x in range(dim)
                if all(clause_satisfied(c, x) for c in clauses)
                and fn(bin(x).count("1"), kk))
        for dk in (1, -1):
            if 0 <= k + dk <= inst.n_problem_qubits:
                out.append((f"popcount bound k={k+dk} instead of {k}",
                            sc_set(k + dk, cmp_)))
        for other in cmp_fns:
            if other != cmp_:
                out.append((f"popcount comparison '{other}' instead of "
                            f"'{cmp_}'", sc_set(k, other)))
        for j, c in enumerate(clauses):
            for lit in range(len(c)):
                f2 = [list(map(list, cc)) for cc in clauses]
                f2[j][lit][1] ^= 1
                out.append((
                    f"literal {lit+1} of clause {j+1} polarity flipped",
                    frozenset(x for x in range(dim)
                              if all(clause_satisfied(cc, x) for cc in f2)
                              and cmp_fns[cmp_](bin(x).count("1"), k))))
    if fam in ("coloring", "latin_square"):
        # C6 signature: non-surjective decode (11 treated as a 4th value)
        if fam == "coloring":
            edges = spec["edges"]
            out.append((
                "NON-SURJECTIVE decode (code 11 treated as a distinct 4th "
                "color instead of color 0)",
                frozenset(x for x in range(dim) if all(
                    ((x >> (2 * a)) & 3) != ((x >> (2 * b)) & 3)
                    for a, b in edges))))
    if fam == "vertex_cover":
        k = spec["k"]
        edges = spec["edges"]

        def vc_set(kk, with_edges=True):
            return frozenset(
                x for x in range(dim)
                if bin(x).count("1") <= kk
                and (not with_edges or all((x >> a) & 1 or (x >> b) & 1
                                           for a, b in edges)))
        out.append((f"size bound k={k+1} instead of {k}", vc_set(k + 1)))
        if k >= 1:
            out.append((f"size bound k={k-1} instead of {k}", vc_set(k - 1)))
        out.append(("size bound IGNORED (only edge coverage checked)",
                    vc_set(inst.n_problem_qubits)))
    if fam == "subset_sum":
        vals, t = spec["values"], spec["target"]

        def ss_set(pred):
            return frozenset(
                x for x in range(dim)
                if pred(sum(v for i, v in enumerate(vals) if (x >> i) & 1)))
        for dt in (1, -1):
            out.append((f"target {t+dt} instead of {t}",
                        ss_set(lambda s, tt=t + dt: s == tt)))
        out.append((f"sum <= {t} instead of == {t}",
                    ss_set(lambda s: s <= t)))
        out.append((f"sum >= {t} instead of == {t}",
                    ss_set(lambda s: s >= t)))
    if fam == "string_match" and not spec["anchored"]:
        p, n = spec["pattern"], spec["n_text"]
        out.append(("ANCHORED match only (offset 0), ignoring other "
                    "offsets",
                    frozenset(x for x in range(dim)
                              if matches_at(x, p, 0))))
    return out


# ---------------------------------------------------------------------------
# main entry
# ---------------------------------------------------------------------------

def diagnose(marked: set[int], inst: TaskInstance,
             solutions: set[int]) -> Diagnosis:
    dim = 1 << inst.n_problem_qubits
    marked = frozenset(marked)
    comp = frozenset(range(dim)) - marked
    # orientation: pick the one closer to the truth (global flip modulo)
    truth = frozenset(solutions)
    m = marked if len(marked ^ truth) <= len(comp ^ truth) else comp

    d = Diagnosis()
    for desc, s in edit_hypotheses(inst):
        if s == m and s != truth:
            d.exact = desc
            break

    agg, preds = constraint_predicates(inst)
    if agg == "and":
        rows = []
        for j, (name, p) in enumerate(preds):
            decisive = [x for x in range(dim)
                        if not p(x) and all(q(x) for i, (_, q) in
                                            enumerate(preds) if i != j)]
            if not decisive:
                continue
            ok = sum(1 for x in decisive if x not in m)
            rows.append((name, ok / len(decisive), len(decisive)))
        sat = [x for x in range(dim) if x in truth]
        d.overall_sat_marked = (sum(1 for x in sat if x in m) / len(sat)
                                if sat else None)
        d.scorecard = sorted(rows, key=lambda r: r[1])
    else:   # OR aggregation (string_match): decisive = matches only at j
        rows = []
        for j, (name, p) in enumerate(preds):
            decisive = [x for x in range(dim)
                        if p(x) and not any(q(x) for i, (_, q) in
                                            enumerate(preds) if i != j)]
            if not decisive:
                continue
            ok = sum(1 for x in decisive if x in m)
            rows.append((name, ok / len(decisive), len(decisive)))
        d.scorecard = sorted(rows, key=lambda r: r[1])
        sat = list(truth)
        d.overall_sat_marked = (sum(1 for x in sat if x in m) / len(sat)
                                if sat else None)

    lines = ["Behavioral diagnosis (computed from your oracle's actual "
             "marking behavior):"]
    if d.exact:
        lines.append(f"- your oracle behaves EXACTLY as if: {d.exact}.")
    if d.scorecard:
        worst = [r for r in d.scorecard if r[1] < 0.999][:MAX_SCORECARD_LINES]
        if worst:
            lines.append("- constraint respect rates (fraction of decisive "
                         "inputs handled correctly):")
            for name, rate, n in worst:
                flag = "  <-- LIKELY BROKEN" if rate < 0.5 else ""
                lines.append(f"    {name}: {rate:.0%} ({n} inputs){flag}")
        else:
            lines.append("- every individual constraint is respected on "
                         "its decisive inputs; the error is in how they "
                         "are COMBINED (or in states violating several "
                         "constraints at once).")
    if d.overall_sat_marked is not None:
        lines.append(f"- satisfying assignments correctly marked: "
                     f"{d.overall_sat_marked:.0%}.")
    d.text = "\n".join(lines)
    return d
