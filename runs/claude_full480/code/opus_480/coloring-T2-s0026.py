from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1),(0,2),(0,4),(1,2),(1,3),(1,4),(2,3),(3,4)]

    def qbits(v):
        return problem_qubits[2*v], problem_qubits[2*v+1]

    # For each edge we compute a "same color" flag into an edge-ancilla.
    # Two vertices share a decoded color iff:
    #   both codes in {00,11} (color 0), or codes equal to 01 (both), or equal to 10 (both).
    # Color of vertex: color0 = (~b0 & ~b1) | (b0 & b1)  [codes 00 or 11]
    #                  color1 = b0 & ~b1                  [code 01]
    #                  color2 = ~b0 & b1                  [code 10]
    # same_color(u,v) = c0u&c0v | c1u&c1v | c2u&c2v
    # We compute same_color into one ancilla per edge, then multi-control-Z
    # over all edge-ancillas being 0 (i.e. no edge monochromatic) -> mark.

    edge_anc = ancilla_qubits[:len(edges)]  # 8 ancillas
    work = ancilla_qubits[len(edges)]       # 1 scratch ancilla (9th)

    def color_flags_compute(v, targets):
        # targets = (t0, t1, t2) receive color0,color1,color2 indicators
        b0, b1 = qbits(v)
        t0, t1, t2 = targets
        # color1 = b0 & ~b1
        qc.x(b1); qc.ccx(b0, b1, t1); qc.x(b1)
        # color2 = ~b0 & b1
        qc.x(b0); qc.ccx(b0, b1, t2); qc.x(b0)
        # color0 = 00 or 11 = NOT(color1 or color2) = NOT(t1 or t2)
        # t0 = 1 initially set, then clear if t1 or t2
        qc.x(t0)
        qc.cx(t1, t0)
        qc.cx(t2, t0)

    def color_flags_uncompute(v, targets):
        b0, b1 = qbits(v)
        t0, t1, t2 = targets
        qc.cx(t2, t0)
        qc.cx(t1, t0)
        qc.x(t0)
        qc.x(b0); qc.ccx(b0, b1, t2); qc.x(b0)
        qc.x(b1); qc.ccx(b0, b1, t1); qc.x(b1)

    # We don't have enough ancillas to hold color flags for all vertices at once,
    # so process each edge independently using the single 'work' ancilla scheme
    # is not enough (need 6 flag qubits). Instead compute same_color directly.
    #
    # same_color via direct construction into edge ancilla e:
    #   e ^= c0u&c0v ; e ^= c1u&c1v ; e ^= c2u&c2v   (these are mutually exclusive,
    #   so XOR == OR). Each term needs the two color indicators AND'd.
    #
    # To avoid needing many scratch qubits simultaneously, we build each product
    # using MCX with the raw code qubits after basis changes, term by term.

    def edge_same_color_compute(u, v, e):
        u0, u1 = qbits(u)
        v0, v1 = qbits(v)
        # Term color1&color1: c1 = b0 & ~b1  => controls: u0=1,u1=0,v0=1,v1=0
        qc.x(u1); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], e)
        qc.x(u1); qc.x(v1)
        # Term color2&color2: c2 = ~b0 & b1 => controls: u0=0,u1=1,v0=0,v1=1
        qc.x(u0); qc.x(v0)
        qc.mcx([u0, u1, v0, v1], e)
        qc.x(u0); qc.x(v0)
        # Term color0&color0: c0 = (00 or 11). Product over u,v with each in {00,11}.
        # This is 2x2 = 4 combinations: (00,00),(00,11),(11,00),(11,11)
        # u in {00,11}: u0==u1. v0==v1. Enumerate 4 patterns.
        # (u0=0,u1=0,v0=0,v1=0)
        qc.x(u0); qc.x(u1); qc.x(v0); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], e)
        qc.x(u0); qc.x(u1); qc.x(v0); qc.x(v1)
        # (u0=0,u1=0,v0=1,v1=1)
        qc.x(u0); qc.x(u1)
        qc.mcx([u0, u1, v0, v1], e)
        qc.x(u0); qc.x(u1)
        # (u0=1,u1=1,v0=0,v1=0)
        qc.x(v0); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], e)
        qc.x(v0); qc.x(v1)
        # (u0=1,u1=1,v0=1,v1=1)
        qc.mcx([u0, u1, v0, v1], e)

    def edge_same_color_uncompute(u, v, e):
        u0, u1 = qbits(u)
        v0, v1 = qbits(v)
        qc.mcx([u0, u1, v0, v1], e)
        qc.x(v0); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], e)
        qc.x(v0); qc.x(v1)
        qc.x(u0); qc.x(u1)
        qc.mcx([u0, u1, v0, v1], e)
        qc.x(u0); qc.x(u1)
        qc.x(u0); qc.x(u1); qc.x(v0); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], e)
        qc.x(u0); qc.x(u1); qc.x(v0); qc.x(v1)
        qc.x(u0); qc.x(v0)
        qc.mcx([u0, u1, v0, v1], e)
        qc.x(u0); qc.x(v0)
        qc.x(u1); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], e)
        qc.x(u1); qc.x(v1)

    # Compute same_color flag for every edge
    for (u, v), e in zip(edges, edge_anc):
        edge_same_color_compute(u, v, e)

    # Valid coloring iff ALL edge flags == 0. Apply phase -1 in that case:
    # flip all edge ancillas, MCP(pi) controlled on all being 1, flip back.
    for e in edge_anc:
        qc.x(e)
    import numpy as np
    qc.mcp(np.pi, edge_anc[:-1], edge_anc[-1])
    for e in edge_anc:
        qc.x(e)

    # Uncompute same_color flags
    for (u, v), e in zip(edges, edge_anc):
        edge_same_color_uncompute(u, v, e)
