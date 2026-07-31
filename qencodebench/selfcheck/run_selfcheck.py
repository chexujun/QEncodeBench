"""Verifier self-check suite.

Checks, in order:
  1. reference oracles pass L3 + L4 for every family x tier x seed sample;
  2. global-phase regression: for each reference, (a) the "-1 on non-solutions"
     variant and (b) an arbitrary-global-phase variant both PASS;
  3. all 16 mutants are rejected, and the two permutation mutants are
     verified to be invisible to the uniform-superposition screen alone;
  4. method agreement: method A vs exhaustive (vs method B when <= 10 qubits)
     agree on every sampled reference and mutant.

Writes a markdown report and exits non-zero on any failure.
"""

from __future__ import annotations

import argparse
import math
import sys
import time

import numpy as np

from qencodebench.core.sim import run_statevector
from qencodebench.core.transpiling import transpile_fixed
from qencodebench.generators import GENERATORS, get_generator
from qencodebench.selfcheck.mutants import build_mutants
from qencodebench.verifier.functional import (
    method_a, exhaustive, method_b, TOL_PHASE,
)

from qiskit import QuantumCircuit


def uniform_screen_passes(circ: QuantumCircuit, n: int,
                          sols: set[int]) -> bool:
    """Steps 1+3 of method A only (no fingerprints) -- used to prove the
    permutation mutants would slip through a single uniform-state check."""
    prep = QuantumCircuit(circ.num_qubits)
    prep.h(range(n))
    prep.compose(circ, inplace=True)
    sv = run_statevector(prep)
    dim = 1 << n
    block = sv[:dim]
    if 1.0 - float(np.sum(np.abs(block) ** 2)) > 1e-9:
        return False
    if float(np.max(np.abs(np.abs(block) - 2 ** (-n / 2)))) > 1e-6:
        return False
    f = np.zeros(dim, dtype=np.int8)
    for s in sols:
        f[s] = 1
    rel = np.angle(block / block[0])
    target = np.pi * (f ^ f[0]).astype(float)
    dev = np.abs(np.angle(np.exp(1j * (rel - target))))
    return float(np.max(dev)) <= TOL_PHASE


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=3,
                    help="reference seeds per family x tier")
    ap.add_argument("--agreement-samples", type=int, default=0,
                    help="extra method-A/exhaustive agreement samples "
                         "(500 are required before enabling the fast path)")
    ap.add_argument("--out", default="analysis/selfcheck_report.md")
    args = ap.parse_args()

    lines = ["# Verifier self-check report", "",
             f"date: {time.strftime('%Y-%m-%d %H:%M:%S')}", ""]
    failures: list[str] = []

    # ---- 1 & 2: references + global-phase regression ----------------------
    lines.append("## 1-2. Reference oracles + global-phase regression")
    n_ref = 0
    for family in GENERATORS:
        for tier in GENERATORS[family].tiers:
            for seed in range(1, args.seeds + 1):
                gen = get_generator(family)
                inst = gen.generate(tier, seed)
                sols = gen.classical_solutions(inst)
                ref = gen.reference_oracle(inst)
                n_ref += 1
                res = method_a(ref, inst.n_problem_qubits, sols)
                if not res.passed:
                    failures.append(f"REF FAIL {inst.task_id}: "
                                    f"{res.fail_reason}")
                depth = transpile_fixed(ref).depth()
                if depth > inst.max_depth or \
                        ref.num_qubits > inst.max_total_qubits:
                    failures.append(f"REF L4 FAIL {inst.task_id}")
                # (a) mark non-solutions instead of solutions (global -1)
                va = ref.copy()
                va.global_phase += math.pi
                # (b) arbitrary global phase
                vb = ref.copy()
                vb.global_phase += 0.73612
                for tag, var in (("-1", va), ("e^i0.736", vb)):
                    r = method_a(var, inst.n_problem_qubits, sols)
                    if not r.passed:
                        failures.append(
                            f"GLOBAL-PHASE FAIL {inst.task_id} [{tag}]: "
                            f"{r.fail_reason}")
    lines.append(f"- references checked: {n_ref} "
                 f"(x3 with the two global-phase variants)")

    # ---- 3: mutants --------------------------------------------------------
    lines.append("")
    lines.append("## 3. Mutant rejection (16 mutants)")
    lines.append("")
    lines.append("| mutant | rejected | fail_reason | mark_accuracy | "
                 "fools uniform screen |")
    lines.append("|---|---|---|---|---|")
    for name, circ, inst, sols in build_mutants():
        res = method_a(circ, inst.n_problem_qubits, sols)
        screen = uniform_screen_passes(circ, inst.n_problem_qubits, sols)
        if res.passed:
            failures.append(f"MUTANT ACCEPTED: {name}")
        if name in ("M13_basis_swap", "M14_phased_3cycle") and not screen:
            failures.append(f"{name} did NOT fool the uniform screen "
                            "(regression intent broken)")
        acc = "" if res.mark_accuracy is None else f"{res.mark_accuracy:.4f}"
        lines.append(f"| {name} | {not res.passed} | {res.fail_reason} "
                     f"| {acc} | {screen} |")

    # ---- 4: method agreement ----------------------------------------------
    lines.append("")
    lines.append("## 4. Method agreement (A vs exhaustive vs B)")
    n_agree = 0
    rng = np.random.default_rng(7)
    todo = []
    for family in GENERATORS:
        for tier in GENERATORS[family].tiers:
            todo.append((family, tier))
    count = 0
    seed = 100
    target = args.agreement_samples
    while count < target:
        family, tier = todo[count % len(todo)]
        gen = get_generator(family)
        try:
            inst = gen.generate(tier, seed + count)
        except RuntimeError:
            count += 1
            continue
        sols = gen.classical_solutions(inst)
        ref = gen.reference_oracle(inst)
        # verify both the reference and a randomly mutated (phase-flipped)
        # variant so agreement covers PASS and FAIL verdicts
        variants = [ref]
        bad = ref.copy()
        bad.z(int(rng.integers(0, inst.n_problem_qubits)))
        variants.append(bad)
        for circ in variants:
            a = method_a(circ, inst.n_problem_qubits, sols)
            ex = exhaustive(circ, inst.n_problem_qubits, sols)
            if a.passed != ex.passed:
                failures.append(
                    f"A/exhaustive disagree on {inst.task_id}: "
                    f"{a.passed} vs {ex.passed}")
            if circ.num_qubits <= 10:
                b = method_b(circ, inst.n_problem_qubits, sols)
                if b != ex.passed:
                    failures.append(
                        f"B/exhaustive disagree on {inst.task_id}")
            n_agree += 1
        count += 1
    lines.append(f"- agreement checks run: {n_agree}")

    # ---- summary ------------------------------------------------------------
    lines.append("")
    lines.append("## Result")
    if failures:
        lines.append(f"**FAILED** ({len(failures)} problems):")
        lines += [f"- {f}" for f in failures]
    else:
        lines.append("**ALL CHECKS PASSED**")

    import os
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines[-min(20, len(lines)):]))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
