from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (1, 3), (1, 4), (2, 4), (3, 4)]
    x = problem_qubits
    n = len(x)

    edge_anc = ancilla_qubits[0:5]
    count_anc = ancilla_qubits[5:8]
    final = None

    def compute():
        # For each edge, mark edge_anc[i] = 1 iff edge covered (u OR v).
        for i, (u, v) in enumerate(edges):
            a = edge_anc[i]
            # OR via De Morgan: a = NOT(NOT u AND NOT v)
            qc.x(x[u]); qc.x(x[v])
            qc.x(a)
            qc.ccx(x[u], x[v], a)
            qc.x(x[u]); qc.x(x[v])

        # Popcount of the 5 problem bits into 3-bit register count_anc (LSB first).
        c0, c1, c2 = count_anc[0], count_anc[1], count_anc[2]
        for i in range(n):
            b = x[i]
            # carry from bit0
            qc.ccx(b, c0, c1)          # c1 gets carry of (b + c0)
            # carry into c2 from c1 addition (only when both b&c0 caused c1 toggle and c1 already set)
            qc.ccx(c1, b, c2) if False else None
            qc.cx(b, c0)               # add b into c0
        # The above simple ripple is insufficient for exact popcount; use full adder chain below instead.

    # Full correct implementation using an explicit incrementer-based popcount.
    def compute_full():
        c0, c1, c2 = count_anc[0], count_anc[1], count_anc[2]
        for i, (u, v) in enumerate(edges):
            a = edge_anc[i]
            qc.x(x[u]); qc.x(x[v])
            qc.x(a)
            qc.ccx(x[u], x[v], a)
            qc.x(x[u]); qc.x(x[v])
        # popcount: for each problem bit, increment the 3-bit counter conditioned on that bit
        for i in range(n):
            b = x[i]
            # increment counter (c2 c1 c0) by 1 when b==1
            # c2 ^= b & c1 & c0 ; c1 ^= b & c0 ; c0 ^= b
            qc.mcx([b, c1, c0], c2)
            qc.ccx(b, c0, c1)
            qc.cx(b, c0)

    def uncompute_full():
        c0, c1, c2 = count_anc[0], count_anc[1], count_anc[2]
        for i in reversed(range(n)):
            b = x[i]
            qc.cx(b, c0)
            qc.ccx(b, c0, c1)
            qc.mcx([b, c1, c0], c2)
        for i, (u, v) in enumerate(edges):
            a = edge_anc[i]
            qc.x(x[u]); qc.x(x[v])
            qc.ccx(x[u], x[v], a)
            qc.x(a)
            qc.x(x[u]); qc.x(x[v])

    compute_full()

    # Predicate: all edges covered (all edge_anc == 1) AND count <= 3.
    # count <= 3 means c2 == 0 (since max count 5; c2 set means count >= 4).
    # So condition = (edge_anc all 1) AND (c2 == 0).
    controls = list(edge_anc)
    qc.x(count_anc[2])                 # so control-on-1 means c2==0
    controls.append(count_anc[2])
    # Apply phase -1 on the all-controls-1 subspace using multi-controlled Z.
    tgt = controls[-1]
    qc.h(tgt)
    qc.mcx(controls[:-1], tgt)
    qc.h(tgt)
    qc.x(count_anc[2])                 # restore

    uncompute_full()
