from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 1), (0, 4), (0, 5), (1, 2), (1, 3), (3, 5)]
    p = problem_qubits
    k = 3
    n = len(p)

    edge_anc = ancilla_qubits[:len(edges)]      # 6 ancillas, one per edge
    count_anc = ancilla_qubits[len(edges):len(edges) + 3]  # 3 ancillas for popcount (values 0..6 need 3 bits)
    flag = ancilla_qubits[-1] if len(ancilla_qubits) > len(edges) + 3 else None

    # We have 9 ancillas: 6 edge + 3 count. Need a phase target.
    # Reuse: compute edge-cover AND into using count ancillas isn't possible simultaneously.
    # Strategy: compute per-edge covered flags, compute popcount<=k flag, combine with multi-controlled phase.

    # --- compute edge covered flags: edge_anc[e] = 1 if edge covered ---
    # covered(u,v) = u OR v = NOT( (NOT u) AND (NOT v) )
    def edge_compute():
        for e, (u, v) in enumerate(edges):
            a = edge_anc[e]
            qc.x(p[u]); qc.x(p[v])
            qc.ccx(p[u], p[v], a)   # a = (NOT u AND NOT v) after the x flips  -> actually a= u_flipped AND v_flipped
            qc.x(p[u]); qc.x(p[v])
            qc.x(a)                 # a = NOT(...) = u OR v = covered

    def edge_uncompute():
        for e, (u, v) in reversed(list(enumerate(edges))):
            a = edge_anc[e]
            qc.x(a)
            qc.x(p[u]); qc.x(p[v])
            qc.ccx(p[u], p[v], a)
            qc.x(p[u]); qc.x(p[v])

    # --- popcount into count_anc (3-bit ripple) : count = sum of p bits ---
    # count_anc bits c0 (LSB), c1, c2. Add each problem bit.
    c0, c1, c2 = count_anc

    def add_bit(b):
        # add problem bit b (control) into 3-bit counter (c0,c1,c2)
        # carry chain: on b, increment counter
        # c2 ^= (b AND c1 AND c0)
        qc.mcx([b, c1, c0], c2)
        # c1 ^= (b AND c0)
        qc.ccx(b, c0, c1)
        # c0 ^= b
        qc.cx(b, c0)

    def add_bit_inv(b):
        qc.cx(b, c0)
        qc.ccx(b, c0, c1)
        qc.mcx([b, c1, c0], c2)

    def count_compute():
        for i in range(n):
            add_bit(p[i])

    def count_uncompute():
        for i in reversed(range(n)):
            add_bit_inv(p[i])

    # size<=3 predicate on 3-bit count (values 0..6):
    # count<=3 means NOT(count>=4) = NOT(c2 AND (c1 OR c0))  ; count>=4 <=> c2 set with c1 or c0, plus 4 itself (100)=4>3
    # Actually count values: 4=100,5=101,6=110. All have c2=1. count=3=011 has c2=0. So count<=3 <=> c2==0.
    # Great: since max count is 6 and 4,5,6 all have bit2=1 and 0..3 have bit2=0, predicate = NOT c2.

    edge_compute()
    count_compute()

    # Phase -1 iff all edges covered AND count<=3 (i.e. c2==0).
    # Controls: all edge_anc == 1, and c2 == 0.
    qc.x(c2)  # so control on c2 meaning c2==0
    controls = list(edge_anc) + [c2]
    qc.h(flag)
    qc.mcx(controls, flag)
    qc.h(flag)
    qc.x(c2)

    count_uncompute()
    edge_uncompute()
