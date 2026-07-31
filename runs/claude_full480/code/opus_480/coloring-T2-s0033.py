from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 3), (1, 3), (2, 3), (2, 4)]

    def qb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # edge_ok[e] ancilla == 1 iff the two endpoints of edge e have DIFFERENT colors.
    # Two vertices share a color iff their decoded colors are equal.
    # Decoding: c in {0,1,2}, and c=3 -> color 0 (same as c=0).
    # So color(a)==color(b) iff:
    #   (a in {00,11} and b in {00,11})  [both color 0]
    #   or (a==01 and b==01)             [both color 1]
    #   or (a==10 and b==10)             [both color 2]
    # We compute a "same" flag per edge, then edge_ok = NOT same.
    # f = AND over edges of edge_ok. Mark f==1 with phase -1.

    edge_ok = ancilla_qubits[:len(edges)]      # 5 ancillas
    final_anc = ancilla_qubits[len(edges)]     # 1 ancilla

    def compute_edge_ok(e, target):
        (a0, a1) = qb(edges[e][0])
        (b0, b1) = qb(edges[e][1])
        # Set target = 1 when colors are the SAME, then we'll flip to get OK.
        # Term1: both color 0 -> a in {00,11}: (a0==a1) i.e. NOT(a0 xor a1);
        #        b in {00,11}: (b0==b1).
        #   sameA0 := a0 xor a1 == 0 ; sameB0 := b0 xor b1 == 0.
        #   Use ancilla-free approach via controlled gates onto target.
        # We build "same" by adding (mod 2 accumulation won't work for OR);
        # instead flip target for each mutually-exclusive same-color case.
        #
        # Case color0: a in {00,11} AND b in {00,11}.
        #   Encode aEq = NOT(a0 xor a1): compute into a1? We must not disturb inputs
        #   irreversibly; use compute/uncompute on scratch bits within target logic.
        # We use target itself and mcx with control-state via x wrappers.

        # color 1: a==01 (a0=1,a1=0) and b==01.
        qc.x(a1); qc.x(b1)
        qc.mcx([a0, a1, b0, b1], target)
        qc.x(a1); qc.x(b1)
        # color 2: a==10 (a0=0,a1=1) and b==10.
        qc.x(a0); qc.x(b0)
        qc.mcx([a0, a1, b0, b1], target)
        qc.x(a0); qc.x(b0)
        # color 0: a in {00,11} and b in {00,11}.
        # a in {00,11} <=> a0==a1 ; b in {00,11} <=> b0==b1.
        # Enumerate the 4 same-color-0 combos: (00,00),(00,11),(11,00),(11,11).
        for (av0, av1) in [(0, 0), (1, 1)]:
            for (bv0, bv1) in [(0, 0), (1, 1)]:
                flips = []
                if av0 == 0: flips.append(a0)
                if av1 == 0: flips.append(a1)
                if bv0 == 0: flips.append(b0)
                if bv1 == 0: flips.append(b1)
                for q in flips: qc.x(q)
                qc.mcx([a0, a1, b0, b1], target)
                for q in flips: qc.x(q)
        # Now target == 1 iff colors SAME. Flip to make it edge_ok (1 iff different).
        qc.x(target)

    def uncompute_edge_ok(e, target):
        (a0, a1) = qb(edges[e][0])
        (b0, b1) = qb(edges[e][1])
        qc.x(target)
        for (av0, av1) in [(1, 1), (0, 0)]:
            for (bv0, bv1) in [(1, 1), (0, 0)]:
                flips = []
                if av0 == 0: flips.append(a0)
                if av1 == 0: flips.append(a1)
                if bv0 == 0: flips.append(b0)
                if bv1 == 0: flips.append(b1)
                for q in flips: qc.x(q)
                qc.mcx([a0, a1, b0, b1], target)
                for q in flips: qc.x(q)
        qc.x(a0); qc.x(b0)
        qc.mcx([a0, a1, b0, b1], target)
        qc.x(a0); qc.x(b0)
        qc.x(a1); qc.x(b1)
        qc.mcx([a0, a1, b0, b1], target)
        qc.x(a1); qc.x(b1)

    # Compute all edge_ok flags.
    for e in range(len(edges)):
        compute_edge_ok(e, edge_ok[e])

    # final_anc = AND of all edge_ok, phase, then uncompute AND.
    qc.h(final_anc)
    qc.mcx(edge_ok, final_anc)
    qc.h(final_anc)

    # Uncompute edge_ok flags in reverse.
    for e in reversed(range(len(edges))):
        uncompute_edge_ok(e, edge_ok[e])
