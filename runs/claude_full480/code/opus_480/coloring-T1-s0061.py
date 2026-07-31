import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits, ancilla_qubits) -> None:
    # Vertex v uses problem_qubits[2v] (b0, low) and problem_qubits[2v+1] (b1, high).
    # Color decoding: c=0->0, c=1->1, c=2->2, c=3->0. So color(0)==color(3).
    # An edge (u,w) is SATISFIED iff color(u) != color(w).
    # f(x)=1 iff ALL edges satisfied. Since all edges touch vertex 3, we compute
    # per-edge "monochromatic?" flags, and require NONE are set.

    edges = [(0, 3), (1, 3), (2, 3)]

    def qb(v, bit):
        return problem_qubits[2 * v + bit]

    # We need an ancilla per edge to hold "edge is monochromatic" (1 = bad).
    # 3 edges -> 3 ancillas as edge flags; 1 ancilla spare (unused, stays |0>).
    edge_anc = [ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]]

    # Helper: compute into target flag whether color(u)==color(w).
    # color(u)==color(w) as codes with c=3 aliased to 0.
    # Equivalent classes over 2-bit code: {00,11}->A(0), {01}->B(1), {10}->C(2).
    # Two vertices share color iff their codes fall in the same class.
    #
    # Define for a vertex the predicates:
    #   isA = (code==00) OR (code==11)  -> b0==b1
    #   isB = (code==01)                -> b0=1,b1=0
    #   isC = (code==10)                -> b0=0,b1=1
    # color(u)==color(w) iff (isA_u & isA_w) | (isB_u & isB_w) | (isC_u & isC_w).
    #
    # isA_v = (b0 == b1) = NOT(b0 XOR b1).
    # We'll build each term into the flag via multi-controlled gates using
    # temporary control conditions. To avoid extra ancillas, we compute each
    # of the three product terms directly onto the edge flag with controls
    # set by X-conditioning, and rely on the fact the three terms are mutually
    # exclusive (a vertex is in exactly one class, so at most one term fires).

    def compute_mono(u, w, flag):
        u0, u1 = qb(u, 0), qb(u, 1)
        w0, w1 = qb(w, 0), qb(w, 1)

        # Term B: isB_u & isB_w = (u0=1,u1=0) & (w0=1,w1=0)
        # controls: u0=1, u1=0, w0=1, w1=0
        qc.x(u1); qc.x(w1)
        qc.mcx([u0, u1, w0, w1], flag)
        qc.x(u1); qc.x(w1)

        # Term C: isC_u & isC_w = (u0=0,u1=1) & (w0=0,w1=1)
        qc.x(u0); qc.x(w0)
        qc.mcx([u0, u1, w0, w1], flag)
        qc.x(u0); qc.x(w0)

        # Term A: isA_u & isA_w = (u0==u1) & (w0==w1).
        # isA_u has two sub-cases (00 and 11); same for w -> 4 combinations.
        # 00_u & 00_w:
        qc.x(u0); qc.x(u1); qc.x(w0); qc.x(w1)
        qc.mcx([u0, u1, w0, w1], flag)
        qc.x(u0); qc.x(u1); qc.x(w0); qc.x(w1)
        # 00_u & 11_w:
        qc.x(u0); qc.x(u1)
        qc.mcx([u0, u1, w0, w1], flag)
        qc.x(u0); qc.x(u1)
        # 11_u & 00_w:
        qc.x(w0); qc.x(w1)
        qc.mcx([u0, u1, w0, w1], flag)
        qc.x(w0); qc.x(w1)
        # 11_u & 11_w:
        qc.mcx([u0, u1, w0, w1], flag)

    # Compute all edge mono-flags.
    for i, (u, w) in enumerate(edges):
        compute_mono(u, w, edge_anc[i])

    # f(x)=1 iff all edges satisfied iff every edge flag == 0.
    # Phase -1 when all flags are 0: apply X to flags, multi-controlled Z, X back.
    qc.x(edge_anc[0]); qc.x(edge_anc[1]); qc.x(edge_anc[2])
    qc.h(edge_anc[2])
    qc.mcx([edge_anc[0], edge_anc[1]], edge_anc[2])
    qc.h(edge_anc[2])
    qc.x(edge_anc[0]); qc.x(edge_anc[1]); qc.x(edge_anc[2])

    # Uncompute edge flags (mirror).
    for i, (u, w) in reversed(list(enumerate(edges))):
        compute_mono(u, w, edge_anc[i])
