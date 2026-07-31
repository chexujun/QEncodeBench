from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 4), (0, 5), (1, 3), (1, 5), (2, 3), (3, 4), (4, 5)]

    def qb(v):
        # (low bit, high bit) for vertex v
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # ancilla layout: a_edge computes per-edge "same color" flag (we want
    # ALL edges different => predicate = AND over edges of (u != v)).
    # We compute per edge an equality flag into an edge-ancilla, then use a
    # big controlled-Z on the negations. To keep ancilla usage low (5 avail),
    # we compute edge flags one at a time into a single scratch and OR-reduce
    # into an accumulator... but cleaner: accumulate count of monochromatic
    # edges != 0 is hard reversibly. Instead use per-edge equality ancilla and
    # a multi-controlled phase on "all edges unequal".
    #
    # Color equality of two vertices under surjective decode (c=3 -> color 0):
    # colors equal iff decode(u)==decode(v). Decode maps 00->0,11->0,01->1,10->2.
    # Represent color-equality as a boolean; compute into scratch ancilla,
    # store equality bit, then we want phase -1 iff ALL edges are unequal, i.e.
    # all equality bits == 0. We can't hold 8 equality bits in 5 ancillas, so
    # process reversibly with an accumulator OR-flag: acc = OR of equalities.
    # Then predicate f = NOT acc. Phase -1 iff acc == 0.
    #
    # Build acc via: for each edge compute eq into scratch, OR into acc, then
    # we must uncompute scratch AFTER phase using the mirror -> but OR is not
    # self-inverse. Use compute-all-then-phase-then-uncompute with a chain:
    # keep each edge's eq on its own scratch is impossible. So use the
    # standard trick: recompute. We compute acc forward, apply phase on acc==0,
    # then uncompute acc by reversing. OR reversal needs the scratch eq bits,
    # so recompute them in reverse order.

    a_scratch = ancilla_qubits[0]  # per-edge equality scratch
    a_acc = ancilla_qubits[1]      # OR-accumulator of "some edge monochromatic"

    def eq_compute(u, v, target):
        # Sets target ^= [decode(u)==decode(v)].
        # decode equal classes: {00,11}->0, {01}->1, {10}->2.
        # Equality holds iff (u in class k) and (v in class k) for same k.
        # Enumerate the 3 classes; for each, flip target if both in that class.
        u0, u1 = qb(u)
        v0, v1 = qb(v)
        # class color0 membership: code in {00,11} == (b0 == b1) == NOT(b0 xor b1)
        # class color1 membership: code == 01 -> b0=1,b1=0
        # class color2 membership: code == 10 -> b0=0,b1=1

        # --- color1: both are 01 (b0=1,b1=0) ---
        qc.x(u1); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], target)
        qc.x(u1); qc.x(v1)

        # --- color2: both are 10 (b0=0,b1=1) ---
        qc.x(u0); qc.x(v0)
        qc.mcx([u0, u1, v0, v1], target)
        qc.x(u0); qc.x(v0)

        # --- color0: both in {00,11}, i.e. (u0==u1) and (v0==v1) ---
        # membership of a vertex in color0 = NOT(b0 xor b1). Compute xor into
        # the code bits? We need a controlled flip conditioned on both members.
        # both members: (u0==u1) AND (v0==v1). Use the xor trick with local
        # temporaries by folding into u0,v0 via cx then restore.
        qc.cx(u1, u0)   # u0 now = u0 xor u1 ; member0(u) == (u0'==0)
        qc.cx(v1, v0)   # v0 now = v0 xor v1 ; member0(v) == (v0'==0)
        qc.x(u0); qc.x(v0)
        qc.ccx(u0, v0, target)
        qc.x(u0); qc.x(v0)
        qc.cx(v1, v0)   # restore
        qc.cx(u1, u0)   # restore

    def eq_forward():
        for (u, v) in edges:
            eq_compute(u, v, a_scratch)          # scratch = eq(edge)
            qc.x(a_scratch)                       # scratch = NOT eq
            qc.x(a_acc)                           # acc -> NOT acc
            qc.ccx(a_scratch, a_acc, a_acc)       # if both -> flip: builds OR
            qc.x(a_acc)
            qc.x(a_scratch)
            eq_compute(u, v, a_scratch)           # uncompute scratch to 0

    def eq_reverse():
        for (u, v) in reversed(edges):
            eq_compute(u, v, a_scratch)
            qc.x(a_scratch)
            qc.x(a_acc)
            qc.ccx(a_scratch, a_acc, a_acc)
            qc.x(a_acc)
            qc.x(a_scratch)
            eq_compute(u, v, a_scratch)

    eq_forward()
    # acc == 1 iff some edge monochromatic. f=1 iff acc==0 -> phase -1 on acc==0.
    qc.x(a_acc)
    qc.z(a_acc)
    qc.x(a_acc)
    eq_reverse()
