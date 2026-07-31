from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 2), (0, 3), (0, 4), (1, 4), (3, 4)]

    def qb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    edge_anc = ancilla_qubits[:len(edges)]      # one ancilla per edge (5)
    flag = ancilla_qubits[5]                     # final phase-flag ancilla

    def compute_edge_same(u, v, anc):
        # Set anc = 1  iff  color(u) == color(v).
        # Color equality with surjective code (11 -> 0, i.e. same as 00):
        # color(u)==color(v) iff the real-color 3-value indices match.
        # Real color index r: 00->0, 11->0, 01->1, 10->2.
        # r(u)==r(v) holds iff:
        #   (both in {00,11})  OR  (both 01)  OR  (both 10).
        u0, u1 = qb(u)
        v0, v1 = qb(v)
        # We build predicate P = (r(u)==r(v)) into anc using compute->flip pattern.
        # Enumerate the equality classes via a small helper on class membership.
        # Class C0 = {00,11}: b0==b1 . Class C1={01}: b0=1,b1=0 . Class C2={10}: b0=0,b1=1.
        #
        # match iff (c0u & c0v) | (c1u & c1v) | (c2u & c2v)
        # where c0 = (b0==b1), c1=(b0 & ~b1), c2=(~b0 & b1).
        #
        # We toggle anc once for each satisfied class term. Terms are mutually
        # exclusive across classes for a fixed vertex, and for the pair at most
        # one class-pair term can be 1, so XOR-accumulation = OR here.

        # Term class0: c0u & c0v, with c0 = NOT(b0 XOR b1).
        # Compute t = b0u xor b1u xor b0v xor b1v ; c0u&c0v true iff both pairs equal.
        # But equality of both pairs is not captured by single parity. Do it directly.

        # --- class 0 term: (u0==u1) AND (v0==v1) ---
        qc.cx(u0, u1)            # u1 = u0 xor u1 ; ==0 means equal
        qc.cx(v0, v1)            # v1 = v0 xor v1
        qc.x(u1); qc.x(v1)       # now u1=1 iff equal, v1=1 iff equal
        qc.ccx(u1, v1, anc)      # anc ^= c0u & c0v
        qc.x(u1); qc.x(v1)
        qc.cx(v0, v1)
        qc.cx(u0, u1)            # restore

        # --- class 1 term: (u0 & ~u1) AND (v0 & ~v1) ---
        qc.x(u1); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], anc)   # anc ^= (u0 & ~u1 & v0 & ~v1)
        qc.x(u1); qc.x(v1)

        # --- class 2 term: (~u0 & u1) AND (~v0 & v1) ---
        qc.x(u0); qc.x(v0)
        qc.mcx([u0, u1, v0, v1], anc)   # anc ^= (~u0 & u1 & ~v0 & v1)
        qc.x(u0); qc.x(v0)

    # Compute per-edge "same-color" flags.
    for (u, v), anc in zip(edges, edge_anc):
        compute_edge_same(u, v, anc)

    # f(x)=1 iff NO edge is monochromatic, i.e. all edge_anc == 0.
    # Flip all edge_anc so that "all satisfied" -> all ones, then multi-controlled Z.
    for anc in edge_anc:
        qc.x(anc)
    # Phase -1 iff all edge_anc == 1 (all edges properly colored).
    qc.h(flag)
    qc.mcx(edge_anc, flag)
    qc.h(flag)
    for anc in edge_anc:
        qc.x(anc)

    # Uncompute per-edge flags (mirror).
    for (u, v), anc in reversed(list(zip(edges, edge_anc))):
        compute_edge_same(u, v, anc)
