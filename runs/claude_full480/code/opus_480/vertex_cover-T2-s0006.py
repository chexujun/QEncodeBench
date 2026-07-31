from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    edges = [(0, 1), (0, 4), (1, 4), (2, 3)]
    edge_anc = ancilla_qubits[0:4]      # one ancilla per edge (OR of endpoints)
    cnt = ancilla_qubits[4:7]           # 3-qubit popcount register (counts up to 5)
    flag = None                         # we phase directly on final MCX target reuse

    # ---- compute: edge coverage into edge_anc (OR = 1 iff covered) ----
    for (u, v), a in zip(edges, edge_anc):
        # OR(x_u, x_v) = NOT( AND(NOT x_u, NOT x_v) )
        qc.x(x[u]); qc.x(x[v])
        qc.ccx(x[u], x[v], a)
        qc.x(a)
        qc.x(x[u]); qc.x(x[v])

    # ---- compute: popcount of the 5 problem bits into cnt (binary, LSB=cnt[0]) ----
    # add each x[i] into the 3-bit counter using ripple increment controlled on x[i]
    def add_bit(ctrl):
        # increment 3-bit counter cnt conditioned on ctrl
        # cnt[2] ^= ctrl & cnt[1] & cnt[0]
        qc.mcx([ctrl, cnt[0], cnt[1]], cnt[2])
        # cnt[1] ^= ctrl & cnt[0]
        qc.ccx(ctrl, cnt[0], cnt[1])
        # cnt[0] ^= ctrl
        qc.cx(ctrl, cnt[0])

    for i in range(5):
        add_bit(x[i])

    # size <= 3  <=>  count in {0,1,2,3}  <=>  NOT (count >= 4) <=> cnt[2]==0
    # cnt max is 5 (101). count>=4 iff cnt[2]==1. So size<=3 iff cnt[2]==0.

    # ---- phase: -1 iff all edges covered AND cnt[2]==0 ----
    # controls: edge_anc all ==1, cnt[2]==0 (flip it to use as positive control)
    qc.x(cnt[2])
    qc.h(edge_anc[3])
    qc.mcx([edge_anc[0], edge_anc[1], edge_anc[2], cnt[2]], edge_anc[3])
    qc.h(edge_anc[3])
    qc.x(cnt[2])

    # ---- uncompute popcount (reverse order) ----
    def unadd_bit(ctrl):
        qc.cx(ctrl, cnt[0])
        qc.ccx(ctrl, cnt[0], cnt[1])
        qc.mcx([ctrl, cnt[0], cnt[1]], cnt[2])

    for i in reversed(range(5)):
        unadd_bit(x[i])

    # ---- uncompute edge coverage (reverse) ----
    for (u, v), a in zip(reversed(edges), reversed(edge_anc)):
        qc.x(x[u]); qc.x(x[v])
        qc.x(a)
        qc.ccx(x[u], x[v], a)
        qc.x(x[u]); qc.x(x[v])
