from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (0, 4), (1, 4), (2, 3), (2, 4), (3, 4)]

    def qb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    edge_anc = ancilla_qubits[0]   # accumulates: set to 1 if ANY edge is monochromatic
    e0 = ancilla_qubits[1]         # scratch: b0 equal
    e1 = ancilla_qubits[2]         # scratch: b1 equal
    both = ancilla_qubits[3]       # scratch: both bits equal (same code)

    def compute_edge(u, v):
        u0, u1 = qb(u)
        v0, v1 = qb(v)
        # e0 = NOT(u0 xor v0) = 1 iff low bits equal
        qc.cx(u0, e0)
        qc.cx(v0, e0)
        qc.x(e0)
        # e1 = 1 iff high bits equal
        qc.cx(u1, e1)
        qc.cx(v1, e1)
        qc.x(e1)
        # both = e0 AND e1 = 1 iff identical 2-bit codes
        qc.ccx(e0, e1, both)

    def uncompute_edge(u, v):
        u0, u1 = qb(u)
        v0, v1 = qb(v)
        qc.ccx(e0, e1, both)
        qc.x(e1)
        qc.cx(v1, e1)
        qc.cx(u1, e1)
        qc.x(e0)
        qc.cx(v0, e0)
        qc.cx(u0, e0)

    # Note on the 11 -> color 0 aliasing:
    # Two codes decode to the SAME color iff they are literally the same
    # 2-bit code (00,01,10 are distinct colors) OR the pair is {00, 11}
    # (both color 0). {01,11},{10,11} etc are different colors.
    # So "monochromatic edge" = (same code) OR (codes are 00 and 11).
    # both == 1 handles "same code" (including 11==11).
    # Remaining case: {00,11}. Detect that explicitly and also fold into edge flag.

    def compute_alias(u, v):
        # alias = 1 iff {code_u, code_v} == {00, 11}
        # i.e. (u==00 and v==11) or (u==11 and v==00)
        # We OR two AND-terms into `both` (reused as the per-edge mono flag holder
        # is `both`; but we need a separate accumulation). Use e0,e1 freed after
        # uncompute; here compute directly onto `both` via two multi-controlled X.
        pass

    # Full per-edge monochromatic detection folded into edge_anc.
    # mono(u,v) = same_code OR pair=={00,11}
    for (u, v) in edges:
        u0, u1 = qb(u)
        v0, v1 = qb(v)

        # term A: same code -> 'both'
        compute_edge(u, v)
        qc.cx(both, edge_anc)          # edge_anc ^= same_code
        uncompute_edge(u, v)

        # term B: (u==00 and v==11): u0=0,u1=0,v0=1,v1=1
        qc.x(u0); qc.x(u1)
        qc.mcx([u0, u1, v0, v1], edge_anc)
        qc.x(u0); qc.x(u1)

        # term C: (u==11 and v==00): u0=1,u1=1,v0=0,v1=0
        qc.x(v0); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], edge_anc)
        qc.x(v0); qc.x(v1)

    # edge_anc == 0 iff NO edge is monochromatic == f(x)==1 (proper coloring).
    # Phase -1 when edge_anc == 0: sandwich Z with X.
    qc.x(edge_anc)
    qc.z(edge_anc)
    qc.x(edge_anc)

    # Uncompute edge_anc (mirror, reverse order).
    for (u, v) in reversed(edges):
        u0, u1 = qb(u)
        v0, v1 = qb(v)

        qc.x(v0); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], edge_anc)
        qc.x(v0); qc.x(v1)

        qc.x(u0); qc.x(u1)
        qc.mcx([u0, u1, v0, v1], edge_anc)
        qc.x(u0); qc.x(u1)

        compute_edge(u, v)
        qc.cx(both, edge_anc)
        uncompute_edge(u, v)
