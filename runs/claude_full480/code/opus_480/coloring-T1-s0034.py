from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 2), (1, 2), (3, 4)]

    # per-edge ancilla: e_ancilla[k] = 1 iff edge k is monochromatic (same color)
    edge_anc = ancilla_qubits[0:3]
    flag = ancilla_qubits[3]

    def vq(v):
        # (low bit, high bit) qubits of vertex v
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    def compute_edge_mono(u, v, anc):
        # Two vertices share a color iff decoded colors equal.
        # Codes: 00->0, 01->1, 10->2, 11->0.
        # Colors equal cases:
        #  color0: code in {00,11}; color1: code==01; color2: code==10.
        # anc = 1 iff same color.
        # We compute by enumerating the color-equality via helper on code bits.
        u0, u1 = vq(u)
        v0, v1 = vq(v)
        # Introduce normalized "is color0" markers using the flag-free trick:
        # Same color iff:
        #   (u is color0 AND v is color0) OR (u==01 AND v==01) OR (u==10 AND v==10)
        # where "color0" = (u0,u1) in {00,11} = (u0 == u1).
        #
        # Term A: both color0 = (u0==u1) AND (v0==v1)
        #   u_c0 marker via: NOT(u0 XOR u1). We use anc bits from problem qubits directly
        #   with controlled logic, uncomputed after.
        #
        # We implement each term as a multi-controlled X onto anc, arranged so terms
        # are mutually exclusive (a given (u,v) pair matches at most one term),
        # hence XOR-accumulation onto anc equals OR.

        # Term B: u==01 and v==01  -> u0=1,u1=0,v0=1,v1=0
        qc.x(u1); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], anc)
        qc.x(u1); qc.x(v1)

        # Term C: u==10 and v==10 -> u0=0,u1=1,v0=0,v1=1
        qc.x(u0); qc.x(v0)
        qc.mcx([u0, u1, v0, v1], anc)
        qc.x(u0); qc.x(v0)

        # Term A: (u0==u1) and (v0==v1)
        # (u0==u1) = NOT(u0 XOR u1). Compute t_u = u0 XOR u1 then require t_u=0.
        # Use v-side similarly with an on-the-fly transform:
        # cx u0->u1 gives u1' = u0 xor u1 (=0 iff color0). Same for v.
        qc.cx(u0, u1)
        qc.cx(v0, v1)
        qc.x(u1); qc.x(v1)          # now u1=1 iff original color0, v1=1 iff color0
        qc.mcx([u1, v1], anc)
        qc.x(u1); qc.x(v1)
        qc.cx(v0, v1)
        qc.cx(u0, u1)

    # compute all edge monochrome flags
    for (u, v), anc in zip(edges, edge_anc):
        compute_edge_mono(u, v, anc)

    # f(x)=1 iff NO edge is monochromatic -> all edge_anc == 0.
    # flip edge_anc, multi-controlled Z when all-zero (i.e. all flipped=1).
    for anc in edge_anc:
        qc.x(anc)
    # phase -1 iff all edge_anc were 0
    qc.h(flag)
    qc.x(flag)
    qc.mcx(edge_anc, flag)
    qc.x(flag)
    qc.h(flag)
    # Above realizes phase kickback: mcx with flag in |-> gives -1 when controls all 1.
    for anc in edge_anc:
        qc.x(anc)

    # uncompute edge flags (mirror)
    for (u, v), anc in reversed(list(zip(edges, edge_anc))):
        compute_edge_mono(u, v, anc)
