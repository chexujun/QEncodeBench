import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 1), (0, 2), (0, 4), (1, 2), (1, 3), (1, 4)]

    def qb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    edge_anc = ancilla_qubits[:6]
    final_anc = ancilla_qubits[6]

    def edge_diff_compute(v, w, anc):
        # anc becomes 1 iff decoded colors of v and w DIFFER.
        # Decode: code 3 (11) maps to color 0 (same as code 0).
        # Build "same color" predicate into anc, then flip so anc=1 means different.
        av0, av1 = qb(v)
        aw0, aw1 = qb(w)
        s = anc

        # We compute "same" into s using a helper flag on final_anc region is not available;
        # instead use direct logic on temporary bits within the two-qubit codes.
        # Same-color condition (with 11->0 collapse):
        #   colorEq iff (cv==cw) OR (cv,cw both in {0,3}) essentially:
        #   both decode equal. Colors: c0={00,11}, c1={01}, c2={10}.
        # Same iff (both in {00,11}) OR (cv==01 and cw==01) OR (cv==10 and cw==10).
        #
        # We'll set s=1 for SAME, using three MCX terms, then X(s) to get DIFFERENT.

        # Term A: both in color1 (01): b0=1,b1=0 for both.
        # controls: av0=1,av1=0,aw0=1,aw1=0
        qc.x(av1); qc.x(aw1)
        qc.mcx([av0, av1, aw0, aw1], s)
        qc.x(av1); qc.x(aw1)

        # Term B: both in color2 (10): b0=0,b1=1 for both.
        qc.x(av0); qc.x(aw0)
        qc.mcx([av0, av1, aw0, aw1], s)
        qc.x(av0); qc.x(aw0)

        # Term C: both in color0 = {00,11}.
        # v in color0 iff (av0==av1). w in color0 iff (aw0==aw1).
        # (av0==av1) = NOT(av0 xor av1). Use equality via: same iff av0==av1.
        # We need s ^= [ (av0==av1) AND (aw0==aw1) ].
        # Compute eqv = (av0==av1) into a temp, eqw into a temp, then ccx into s.
        # Temps: reuse other edge ancillas not yet used? Simpler: use two scratch
        # qubits from ancilla pool distinct from s. We'll borrow final_anc + one more.
        # To stay safe, compute in place using the code qubits themselves.
        #
        # eq(a,b) = 1 iff a==b. Put eq into b via: b ^= a (b now = a xor b),
        # then eq = NOT b. So after cx(a,b), b==0 means equal.
        # We do: cx(av0->av1): av1 = av0 xor av1 -> 0 iff equal.
        #        cx(aw0->aw1): aw1 = aw0 xor aw1 -> 0 iff equal.
        # Then both-equal iff av1==0 and aw1==0 -> X both, ccx into s, X back.
        qc.cx(av0, av1)
        qc.cx(aw0, aw1)
        qc.x(av1); qc.x(aw1)
        qc.mcx([av1, aw1], s)
        qc.x(av1); qc.x(aw1)
        qc.cx(aw0, aw1)
        qc.cx(av0, av1)

        # Now s = 1 iff SAME color. Flip to get DIFFERENT.
        qc.x(s)

    # Compute each edge's "different" flag.
    for (v, w), anc in zip(edges, edge_anc):
        edge_diff_compute(v, w, anc)

    # f(x)=1 iff ALL edges different, i.e. all edge_anc == 1.
    qc.h(final_anc)
    qc.mcx(edge_anc, final_anc)
    qc.h(final_anc)

    # Uncompute edge flags (mirror).
    for (v, w), anc in reversed(list(zip(edges, edge_anc))):
        av0, av1 = qb(v)
        aw0, aw1 = qb(w)
        s = anc
        qc.x(s)
        qc.cx(av0, av1)
        qc.cx(aw0, aw1)
        qc.x(av1); qc.x(aw1)
        qc.mcx([av1, aw1], s)
        qc.x(av1); qc.x(aw1)
        qc.cx(aw0, aw1)
        qc.cx(av0, av1)
        qc.x(av0); qc.x(aw0)
        qc.mcx([av0, av1, aw0, aw1], s)
        qc.x(av0); qc.x(aw0)
        qc.x(av1); qc.x(aw1)
        qc.mcx([av0, av1, aw0, aw1], s)
        qc.x(av1); qc.x(aw1)
