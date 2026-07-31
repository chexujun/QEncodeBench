from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (0, 4), (1, 2), (1, 4), (2, 3), (2, 4)]

    def code_qubits(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    edge_anc = ancilla_qubits[:6]
    final_anc = ancilla_qubits[6]

    def edge_diff_compute(v, w, anc):
        # anc becomes 1 iff colors of v and w DIFFER.
        # color(v)==color(w) iff decoded colors equal.
        # decode: c in {0,1,2}, and c=3 -> 0.
        # Approach: compute "same color" into anc via helper, then X.
        (a0, a1) = code_qubits(v)
        (b0, b1) = code_qubits(w)
        # We build "same color" predicate using additional scratch on anc only.
        # same iff decode(v)==decode(w).
        # Equivalent boolean over 4 bits. We compute directly:
        # decode value d(a1,a0): (a1,a0)=00->0,01->1,10->2,11->0
        # so d==0 iff (a0==0 and a1==0) or (a0==1 and a1==1) i.e. a0==a1
        # d==1 iff a0==1,a1==0
        # d==2 iff a0==0,a1==1
        # same color iff (dv==0 and dw==0) or (dv==1 and dw==1) or (dv==2 and dw==2)
        # dv==0 : a0==a1 ; dw==0: b0==b1
        # dv==1 : a0 & ~a1 ; dw==1: b0 & ~b1
        # dv==2 : ~a0 & a1 ; dw==2: ~b0 & b1
        pass

    # We instead compute f directly: f=1 iff all edges proper.
    # per edge: proper iff colors differ. edge_anc[i]=1 iff edge i proper.
    # Then MCX all edge_anc -> final; Z(final); uncompute.

    def set_same(v, w, anc):
        # Flip anc for each of the 3 "same color" conjunctions.
        (a0, a1) = code_qubits(v)
        (b0, b1) = code_qubits(w)
        # dv==0 & dw==0 : (a0==a1) & (b0==b1)
        # Use CCX with controls on equality; equality a0==a1 needs scratch.
        # Simpler: enumerate the 3 same-color color classes explicitly using
        # control states via x-conjugation on the 4 code bits.
        # color 0 for v: (a0,a1) in {00,11}; color0 for w: {00,11}
        # color1 for v: (a0,a1)=10 (a0=1,a1=0); w same
        # color2 for v: (a0,a1)=01 (a0=0,a1=1); w same
        # anc ^= OR over same-color -> but ORs overlap? color classes of v are
        # disjoint, of w disjoint, so the 3 conjunctions (same class both) are
        # mutually exclusive -> XOR == OR. Good.

        # color1 both: a0=1,a1=0,b0=1,b1=0
        qc.x(a1); qc.x(b1)
        qc.mcx([a0, a1, b0, b1], anc)
        qc.x(a1); qc.x(b1)

        # color2 both: a0=0,a1=1,b0=0,b1=1
        qc.x(a0); qc.x(b0)
        qc.mcx([a0, a1, b0, b1], anc)
        qc.x(a0); qc.x(b0)

        # color0 both: v in {00,11}, w in {00,11} -> 4 combos
        for (va0, va1) in [(0, 0), (1, 1)]:
            for (wb0, wb1) in [(0, 0), (1, 1)]:
                flips = []
                if va0 == 0: flips.append(a0)
                if va1 == 0: flips.append(a1)
                if wb0 == 0: flips.append(b0)
                if wb1 == 0: flips.append(b1)
                for q in flips: qc.x(q)
                qc.mcx([a0, a1, b0, b1], anc)
                for q in flips: qc.x(q)

    # compute per-edge "same" into edge_anc, then invert to get "proper"
    for i, (v, w) in enumerate(edges):
        set_same(v, w, edge_anc[i])
        qc.x(edge_anc[i])  # now edge_anc[i]=1 iff proper

    # final = AND of all proper flags
    qc.mcx(edge_anc, final_anc)
    qc.z(final_anc)
    qc.mcx(edge_anc, final_anc)

    # uncompute edges (mirror)
    for i, (v, w) in enumerate(edges):
        qc.x(edge_anc[i])
        set_same(v, w, edge_anc[i])
