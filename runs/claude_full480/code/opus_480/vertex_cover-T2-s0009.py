from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    p = problem_qubits
    edges = [(0, 3), (0, 4), (1, 2), (1, 3), (2, 3), (3, 4)]

    # Ancilla layout:
    #   edge_anc[j] for j in range(6): edge j is covered (OR of endpoints)
    #   size_anc = ancilla_qubits[6..8]: 3-bit popcount of x (max popcount 5 needs 3 bits)
    #   flag ancilla reused = size handling done combinationally; we use one final target.
    edge_anc = ancilla_qubits[0:6]
    s0, s1, s2 = ancilla_qubits[6], ancilla_qubits[7], ancilla_qubits[8]

    def compute_edges():
        for j, (u, v) in enumerate(edges):
            a = edge_anc[j]
            # a = u OR v = NOT((NOT u) AND (NOT v))
            qc.x(p[u]); qc.x(p[v])
            qc.ccx(p[u], p[v], a)
            qc.x(p[u]); qc.x(p[v])
            qc.x(a)

    def uncompute_edges():
        for j, (u, v) in reversed(list(enumerate(edges))):
            a = edge_anc[j]
            qc.x(a)
            qc.x(p[u]); qc.x(p[v])
            qc.ccx(p[u], p[v], a)
            qc.x(p[u]); qc.x(p[v])

    # Ripple popcount of the 5 problem bits into (s2 s1 s0), a 3-bit counter.
    def add_bit(bit):
        # add problem bit `bit` into counter (s0 low bit).
        # carry into s1: s0 & bit ; carry into s2: s1 & (that carry)
        qc.ccx(s1, s0, s2)   # if s1&s0 set and incoming... handled by sequence below
    # Instead implement a clean sequential increment per set bit using full-adder chain.

    def build_counter():
        for b in p:
            # increment 3-bit counter by problem bit b (add b to s0 with carries)
            qc.ccx(s1, s0, s2)  # placeholder replaced below
    # (counter built inline in main body)

    compute_edges()

    # Build 3-bit popcount via successive controlled increments.
    for b in p:
        # add b: carry2 = b & s0 & s1 ; carry1 = b & s0 ; s0 ^= b
        qc.mcx([b, s0, s1], s2)
        qc.ccx(b, s0, s1)
        qc.cx(b, s0)

    # Predicate: all edges covered AND popcount <= 3.
    # popcount <= 3 means NOT(count >= 4) = NOT(s2 AND (s1 OR s0)) ... but max count 5 -> bits.
    # count>=4 iff s2==1 and (s1==1 or s0==1) is wrong; 4=100,5=101 -> s2==1 always means >=4.
    # So popcount<=3 iff s2 == 0.
    controls = list(edge_anc) + [s2]
    qc.x(s2)  # want s2==0 -> control on flipped
    qc.h(controls[-1])
    qc.mcx(controls[:-1], controls[-1])
    qc.h(controls[-1])
    qc.x(s2)

    # Uncompute counter (reverse).
    for b in reversed(p):
        qc.cx(b, s0)
        qc.ccx(b, s0, s1)
        qc.mcx([b, s0, s1], s2)

    uncompute_edges()
