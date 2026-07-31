from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 3), (1, 3), (2, 4), (3, 4)]
    # One ancilla per edge holds "colors differ on this edge" = 1.
    # There are 4 edges and 5 ancillas -> one ancilla per edge, plus none spare.
    assert len(ancilla_qubits) >= len(edges)
    diff_anc = ancilla_qubits[:len(edges)]

    def pins(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # "same color" patterns for an edge (u,v): the set of (uc,vc) 2-bit code
    # combos that decode to the SAME color. Colors: 0<-{00,11}, 1<-{01}, 2<-{10}.
    # code bits: b0 low index, b1 high index; we store as (b0,b1).
    color_codes = {
        0: [(0, 0), (1, 1)],   # b0,b1
        1: [(1, 0)],
        2: [(0, 1)],
    }

    def set_pattern(u0, u1, uc, v0, v1, vc):
        # X the qubits whose desired value is 0 so an all-controls-1 mcx
        # triggers exactly on this code combo.
        flips = []
        for q, bit in ((u0, uc[0]), (u1, uc[1]), (v0, vc[0]), (v1, vc[1])):
            if bit == 0:
                flips.append(q)
        for q in flips:
            qc.x(q)
        return flips

    def compute_edge(edge, anc):
        u, v = edge
        u0, u1 = pins(u)
        v0, v1 = pins(v)
        # anc starts |0>. We want anc = 1 iff colors DIFFER.
        # Easier: set anc=1 for every SAME-color combo, then X to invert.
        for color, combos in color_codes.items():
            for uc in combos:
                for vc in combos:
                    flips = set_pattern(u0, u1, uc, v0, v1, vc)
                    qc.mcx([u0, u1, v0, v1], anc)
                    for q in flips:
                        qc.x(q)
        qc.x(anc)   # invert: anc = 1 iff colors differ

    def uncompute_edge(edge, anc):
        u, v = edge
        u0, u1 = pins(u)
        v0, v1 = pins(v)
        qc.x(anc)
        for color, combos in color_codes.items():
            for uc in combos:
                for vc in combos:
                    flips = set_pattern(u0, u1, uc, v0, v1, vc)
                    qc.mcx([u0, u1, v0, v1], anc)
                    for q in flips:
                        qc.x(q)

    for edge, anc in zip(edges, diff_anc):
        compute_edge(edge, anc)

    # Phase -1 iff every edge's diff ancilla is 1 (all edges properly colored).
    if len(diff_anc) == 1:
        qc.z(diff_anc[0])
    else:
        qc.h(diff_anc[-1])
        qc.mcx(diff_anc[:-1], diff_anc[-1])
        qc.h(diff_anc[-1])

    for edge, anc in reversed(list(zip(edges, diff_anc))):
        uncompute_edge(edge, anc)
