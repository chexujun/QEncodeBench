from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 3), (1, 3), (2, 3)]

    def qbits(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # a0,a1,a2: counter of monochromatic edges (0..4). a3,a4: scratch.
    c0, c1, c2 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]
    m = ancilla_qubits[3]     # per-edge mono flag
    t = ancilla_qubits[4]     # scratch for effective-bit comparison

    def eff0_xor(u, v, tgt):   # tgt ^= eff0_u ^ eff0_v, eff0 = b0 & ~b1
        for w in (u, v):
            b0, b1 = qbits(w)
            qc.x(b1); qc.ccx(b0, b1, tgt); qc.x(b1)

    def eff1_xor(u, v, tgt):   # tgt ^= eff1_u ^ eff1_v, eff1 = b1 & ~b0
        for w in (u, v):
            b0, b1 = qbits(w)
            qc.x(b0); qc.ccx(b1, b0, tgt); qc.x(b0)

    def set_mono(u, v):
        # m ^= [colors equal] = [d0==0 and d1==0]
        eff0_xor(u, v, t)     # t = d0
        eff1_xor(u, v, m)     # m = d1   (temporarily)
        # want m_final = (t==0)&(m==0). Currently m=d1, t=d0.
        # mono = ~d0 & ~d1. Negate both, Toffoli into a fresh? none free.
        # Move: put mono into t using m and vertices, then swap roles.
        # Compute mono into a counter-carry directly instead of storing m.
        raise RuntimeError

    # Because storing mono AND running a controlled increment needs more room,
    # fold them: increment counter directly conditioned on (~d0 & ~d1).
    def add_edge(u, v):
        eff0_xor(u, v, t)          # t = d0
        eff1_xor(u, v, m)          # m = d1
        qc.x(t); qc.x(m)           # t=~d0, m=~d1 ; mono = t & m
        # controlled increment on (t & m):
        qc.mcx([t, m, c1, c0], c2)   # carry to c2
        qc.mcx([t, m, c0], c1)       # carry to c1
        qc.ccx(t, m, c0)             # bump c0
        qc.x(m); qc.x(t)             # restore
        eff1_xor(u, v, m)          # m back to 0
        eff0_xor(u, v, t)          # t back to 0

    def del_edge(u, v):
        eff0_xor(u, v, t)
        eff1_xor(u, v, m)
        qc.x(t); qc.x(m)
        qc.ccx(t, m, c0)
        qc.mcx([t, m, c0], c1)
        qc.mcx([t, m, c1, c0], c2)
        qc.x(m); qc.x(t)
        eff1_xor(u, v, m)
        eff0_xor(u, v, t)

    for (u, v) in edges:
        add_edge(u, v)

    # counter now holds number of monochromatic edges. f=1 iff count==0,
    # i.e. c2=c1=c0=0. Apply phase -1 on that state: X all, mcp(pi), X all.
    qc.x(c0); qc.x(c1); qc.x(c2)
    qc.h(c2)
    qc.mcx([c0, c1], c2)
    qc.h(c2)
    qc.x(c2); qc.x(c1); qc.x(c0)

    for (u, v) in reversed(edges):
        del_edge(u, v)
