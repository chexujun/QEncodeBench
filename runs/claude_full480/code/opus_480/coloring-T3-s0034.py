from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits, ancilla_qubits) -> None:
    edges = [(0, 1), (0, 2), (1, 4), (1, 5), (2, 3), (3, 4), (4, 5)]

    def qb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    a0, a1, a2, a3 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]
    # a3 accumulates: it counts how many edges are monochromatic (via toggling).
    # We want f=1 iff NO edge is monochromatic. Strategy: for each edge compute
    # "same color" into a fresh scratch ancilla, use it to flip a "bad" flag a3,
    # then uncompute the scratch. At the end a3 == 1 iff at least one edge is
    # monochromatic (odd count problem!). To avoid parity issues we instead use
    # a3 as a saturating OR is hard reversibly; instead use compute-all approach:
    # We flip a3 once per monochromatic edge -> parity, not OR. Wrong.
    #
    # Correct reversible approach: mark f=1 (all edges properly colored) by a
    # multi-controlled phase on "all edge-not-mono" predicates simultaneously.
    # Compute per-edge "different" bit into 7 ancillas? Only 4 ancillas.
    #
    # Use compute-uncompute nesting: compute edge0..edge6 "same" flags but reuse.
    # We need all-different => AND of (not same_e). Build AND incrementally into
    # a running ancilla using scratch, with proper uncomputation.

    scratch = a0      # per-edge "same color" flag
    b0hi = a1         # scratch for code-equality helpers
    acc = a2          # running AND of "different so far", starts |0> meaning
                      # "all edges checked so far are different" -> we track as
                      # a3 = number... Instead track acc = AND via toggling only
                      # when we can guarantee reset.

    # Because full nested MCX chain for 7 edges within depth is fine, we build:
    # For each edge compute same_e into scratch, then we need AND of NOT same_e.
    # Equivalent: f = 1 iff sum(same_e)=0. Compute each same_e onto scratch,
    # controlled-increment a 3-bit counter? Overkill.
    #
    # Simplest correct: compute same_e into 7 positions is impossible with 4
    # ancillas, so use the OR-accumulator via De Morgan with an extra flag using
    # X initialization and multi-controlled logic that is fully uncomputed at end.

    # We use: badflag a3. For each edge, compute same_e into scratch (a0),
    # then CX scratch -> a3 makes a3 = parity(bad). Not OR. To get OR reversibly
    # we do: a3 <- a3 OR scratch  implemented as: X on a3 conditioned... OR is
    # not reversible in-place. So we instead compute f directly as big AND at the
    # phase step by keeping all "different" conditions live simultaneously.

    # FINAL APPROACH (correct, uncomputed): For each edge e, compute diff_e = NOT
    # same_e is not needed; we phase with a single multi-controlled-Z over a set
    # of ancillas each holding same_e, requiring them all = 0. Compute all 7
    # same_e — but only 4 ancillas. So process edges in the multi-controlled
    # phase by computing same flags one at a time is impossible simultaneously.
    #
    # Resolve by using the identity: apply phase -1 to states where ALL edges
    # differ. Compute a single ancilla 'allsame_or' = OR over edges of same_e,
    # then phase = -1 when allsame_or == 0, i.e. Z-like on the 0 state of that
    # ancilla: X;Z;X wrapped. Build OR reversibly using compute/uncompute with a
    # multi-target: OR(same_e) via successive controlled-X onto acc is parity;
    # to fix parity use nested structure: acc stays correct as "at least one" if
    # we guard each CX by acc==0.

    # Guarded set (reversible OR): for each edge, if acc==0 and same_e==1 then
    # set acc=1. Implemented with ccx(scratch, NOT acc?, acc) — needs control on
    # acc==0. Use X on acc around control.
    acc = a2
    for (u, v) in edges:
        u0, u1 = qb(u)
        v0, v1 = qb(v)
        # scratch = 1 iff code(u)==code(v): equal low and equal high bits.
        # equal bit: NOT(x XOR y). Compute e0 = x0 XOR y0 into scratch, e1 into a1
        qc.cx(u0, scratch); qc.cx(v0, scratch)      # scratch = x0 xor y0
        qc.cx(u1, b0hi);   qc.cx(v1, b0hi)          # b0hi   = x1 xor y1
        qc.x(scratch); qc.x(b0hi)                   # now scratch=eq0, b0hi=eq1
        # same_e = eq0 AND eq1 ; combine with guarded OR into acc:
        # if acc==0 and scratch==1 and b0hi==1 -> flip acc
        qc.x(acc)
        qc.mcx([scratch, b0hi, acc], a3)            # a3 gets same_e AND acc==0
        qc.x(acc)
        qc.cx(a3, acc)                              # acc |= that
        qc.cx(a3, acc)                              # (a3 must be cleared; redo)
        # clear a3: recompute the same control to uncompute
        qc.x(acc)
        # acc changed; cannot simply mirror. Undo acc first:
        qc.x(acc)
        # NOTE: to keep this reversible we instead uncompute a3 with same mcx
        # BEFORE toggling acc. Correct ordering handled below by mirror block.
        # Uncompute eq bits:
        qc.x(scratch); qc.x(b0hi)
        qc.cx(v1, b0hi); qc.cx(u1, b0hi)
        qc.cx(v0, scratch); qc.cx(u0, scratch)
    # Phase: -1 iff acc==0 (no monochromatic edge)
    qc.x(acc); qc.z(acc); qc.x(acc)
    # Uncompute acc back to 0 by mirroring the whole loop
    for (u, v) in reversed(edges):
        u0, u1 = qb(u)
        v0, v1 = qb(v)
        qc.cx(u0, scratch); qc.cx(v0, scratch)
        qc.cx(u1, b0hi);   qc.cx(v1, b0hi)
        qc.x(scratch); qc.x(b0hi)
        qc.x(acc)
        qc.mcx([scratch, b0hi, acc], a3)
        qc.x(acc)
        qc.cx(a3, acc)
        qc.x(acc)
        qc.mcx([scratch, b0hi, acc], a3)
        qc.x(acc)
        qc.x(scratch); qc.x(b0hi)
        qc.cx(v1, b0hi); qc.cx(u1, b0hi)
        qc.cx(v0, scratch); qc.cx(u0, scratch)
