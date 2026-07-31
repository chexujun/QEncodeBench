import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 3), (1, 2), (1, 3), (2, 3)]

    def vq(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    edge_anc = ancilla_qubits[:len(edges)]  # 4 ancillas, one per edge "same-color" flag
    out = ancilla_qubits[len(edges)]        # final flag

    def edge_same(u, v, anc, invert):
        # Set anc = 1 iff u and v decode to the SAME color.
        # Colors: c in {0,1,2}, with code 3 mapping to color 0.
        # u,v qubits
        u0, u1 = vq(u)
        v0, v1 = vq(v)
        # "u is color0" means code in {00, 11} i.e. u0 == u1.
        # We enumerate the 3 colors and OR together the "both are color k" terms.
        # color0: u0==u1 AND v0==v1
        # color1: (u0=1,u1=0) AND (v0=1,v1=0)
        # color2: (u0=0,u1=1) AND (v0=0,v1=1)
        # Build each conjunction into anc via multi-controlled X, using X-masks;
        # ORing distinct terms is fine because the three color-classes are
        # mutually exclusive, so at most one term fires -> anc gets XORed once.

        # color1: u0=1,u1=0,v0=1,v1=0  -> controls with u1,v1 negated
        for q in (u1, v1):
            qc.x(q)
        qc.mcx([u0, u1, v0, v1], anc)
        for q in (u1, v1):
            qc.x(q)

        # color2: u0=0,u1=1,v0=0,v1=1  -> controls with u0,v0 negated
        for q in (u0, v0):
            qc.x(q)
        qc.mcx([u0, u1, v0, v1], anc)
        for q in (u0, v0):
            qc.x(q)

        # color0: u0==u1 AND v0==v1.
        # u0==u1 iff (u0 xor u1)==0.  Compute parity into u1? We must not disturb
        # inputs. Instead enumerate the two subcases: (00,00),(00,11),(11,00),(11,11).
        for (mu, mv) in [(0, 0), (0, 1), (1, 0), (1, 1)]:
            # mu=0 -> u=00, mu=1 -> u=11 ; similarly mv
            flips = []
            if mu == 0:
                flips += [u0, u1]
            if mv == 0:
                flips += [v0, v1]
            for q in flips:
                qc.x(q)
            qc.mcx([u0, u1, v0, v1], anc)
            for q in flips:
                qc.x(q)

    # Compute: each edge flag = 1 iff endpoints same color (BAD edge).
    for (u, v), anc in zip(edges, edge_anc):
        edge_same(u, v, anc, False)

    # f(x)=1 iff NO edge is monochromatic, i.e. all edge flags == 0.
    # out via multi-controlled: negate all flags, MCX -> out=1 iff all flags 0.
    for anc in edge_anc:
        qc.x(anc)
    qc.mcx(edge_anc, out)
    for anc in edge_anc:
        qc.x(anc)

    # Phase: -1 iff out==1.
    qc.z(out)

    # Uncompute out.
    for anc in edge_anc:
        qc.x(anc)
    qc.mcx(edge_anc, out)
    for anc in edge_anc:
        qc.x(anc)

    # Uncompute edge flags (mirror).
    for (u, v), anc in reversed(list(zip(edges, edge_anc))):
        edge_same(u, v, anc, False)
