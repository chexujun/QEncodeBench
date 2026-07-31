import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits, ancilla_qubits) -> None:
    edges = [(0, 1), (0, 4), (1, 4), (2, 3)]

    def qb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # For each edge, compute an ancilla = 1 iff the two endpoints have the SAME color.
    # Colors: c=0(00), c=1(01), c=2(10), c=3(11)->color 0.
    # So "same color" means: codes equal, OR one is 00 and other is 11, OR one is 11 and other is 00.
    # Equivalent: color(u)==color(v).
    # Represent color equality via a small computation into an edge ancilla.

    edge_ancillas = [ancilla_qubits[i] for i in range(len(edges))]

    def color_same(u, v, out, uncompute=False):
        # u,v are vertices; out is target ancilla set to 1 iff same color.
        u0, u1 = qb(u)
        v0, v1 = qb(v)
        # color(u) as a value in {0,1,2}: cu = (u1,u0) with 11->00.
        # Same color conditions enumerated as products of literals.
        # color 0: codes in {00,11}; color 1: {01}; color 2: {10}.
        # same iff (both color0) or (both color1) or (both color2).
        #
        # both color1: u0=1,u1=0 and v0=1,v1=0
        # both color2: u0=0,u1=1 and v0=0,v1=1
        # both color0: u in {00,11} and v in {00,11}
        #   u is color0 iff (u0==u1). v color0 iff (v0==v1).
        #
        # We compute three partial-product terms into out via multi-controlled X,
        # using X gates to set control polarities. These terms are mutually exclusive,
        # so XOR-ing them into out is fine (out = OR since disjoint).
        seq = []

        # term both color1: u0=1,u1=0,v0=1,v1=0
        seq.append(([ (u0,1),(u1,0),(v0,1),(v1,0) ]))
        # term both color2: u0=0,u1=1,v0=0,v1=1
        seq.append(([ (u0,0),(u1,1),(v0,0),(v1,1) ]))
        # both color0: u0==u1 and v0==v1. Split into 4 disjoint sub-terms:
        #   (u0,u1) in {00,11} x (v0,v1) in {00,11}
        seq.append(([ (u0,0),(u1,0),(v0,0),(v1,0) ]))
        seq.append(([ (u0,0),(u1,0),(v0,1),(v1,1) ]))
        seq.append(([ (u0,1),(u1,1),(v0,0),(v1,0) ]))
        seq.append(([ (u0,1),(u1,1),(v0,1),(v1,1) ]))

        for term in seq:
            ctrls = [q for (q, pol) in term]
            zeros = [q for (q, pol) in term if pol == 0]
            for q in zeros:
                qc.x(q)
            qc.mcx(ctrls, out)
            for q in zeros:
                qc.x(q)

    # Compute all edge "same-color" ancillas.
    for (u, v), out in zip(edges, edge_ancillas):
        color_same(u, v, out)

    # f(x)=1 iff NO edge is monochromatic, i.e. all edge ancillas are 0.
    # Apply phase -1 iff all edge_ancillas == 0.
    for a in edge_ancillas:
        qc.x(a)
    qc.h(edge_ancillas[-1])
    qc.mcx(edge_ancillas[:-1], edge_ancillas[-1])
    qc.h(edge_ancillas[-1])
    for a in edge_ancillas:
        qc.x(a)

    # Uncompute edge ancillas (mirror).
    for (u, v), out in reversed(list(zip(edges, edge_ancillas))):
        color_same(u, v, out)
