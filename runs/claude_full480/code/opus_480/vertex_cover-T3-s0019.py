from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 2), (0, 4), (0, 5), (1, 2), (1, 3), (1, 5), (2, 4), (2, 5), (4, 5)]
    n = len(problem_qubits)

    # ancilla layout: 9 edge ancillas + count register + one phase-target-ish ancilla
    edge_anc = ancilla_qubits[0:9]          # one per edge
    cover_anc = ancilla_qubits[9]           # =1 iff ALL edges covered
    # count register: number of 1-bits among problem qubits, needs ceil(log2(6+1)) = 3 bits
    cnt = ancilla_qubits[10:13]             # wait, only 12 ancillas total -> indices 0..11

    # Re-plan with exactly 12 ancillas (indices 0..11):
    #   0..8  : edge ancillas (9)
    #   9,10,11 : 3-bit counter
    # We need a cover flag too but can avoid a dedicated one by combining.
    edge_anc = ancilla_qubits[0:9]
    cnt = ancilla_qubits[9:12]              # 3-bit binary counter for popcount (max 6 -> fits in 3 bits)

    def compute_edges():
        # edge ancilla = OR(u,v) = NOT(AND(NOT u, NOT v))
        for j, (u, v) in enumerate(edges):
            a = edge_anc[j]
            qu, qv = problem_qubits[u], problem_qubits[v]
            qc.x(qu); qc.x(qv)
            qc.x(a)
            qc.ccx(qu, qv, a)   # a = 1 XOR (NOTu AND NOTv) = OR(u,v)
            qc.x(qu); qc.x(qv)

    def uncompute_edges():
        for j in range(len(edges) - 1, -1, -1):
            u, v = edges[j]
            a = edge_anc[j]
            qu, qv = problem_qubits[u], problem_qubits[v]
            qc.x(qu); qc.x(qv)
            qc.ccx(qu, qv, a)
            qc.x(a)
            qc.x(qu); qc.x(qv)

    def add_counter():
        # ripple-increment counter by each problem qubit (controlled increment)
        # cnt[0]=LSB, cnt[1], cnt[2]=MSB ; add 1 controlled on each problem qubit
        for i in range(n):
            c = problem_qubits[i]
            # increment 3-bit counter controlled on c
            # carry into bit2: if c & cnt0 & cnt1 -> flip cnt2
            qc.mcx([c, cnt[0], cnt[1]], cnt[2])
            # carry into bit1: if c & cnt0 -> flip cnt1
            qc.ccx(c, cnt[0], cnt[1])
            # bit0: flip cnt0 controlled on c
            qc.cx(c, cnt[0])

    def uncompute_counter():
        for i in range(n - 1, -1, -1):
            c = problem_qubits[i]
            qc.cx(c, cnt[0])
            qc.ccx(c, cnt[0], cnt[1])
            qc.mcx([c, cnt[0], cnt[1]], cnt[2])

    # ----- COMPUTE -----
    compute_edges()
    add_counter()

    # ----- PHASE -----
    # Predicate: all edges covered AND count <= 4.
    # all edges covered = product over edge_anc == 1 (all edge ancillas are 1).
    # count <= 4  <=> NOT(count >= 5) <=> NOT(count in {5,6}).
    # count>=5 means MSB(cnt2)=1 AND (cnt1=1)  [5=101,6=110]; 5=101 -> cnt2=1,cnt1=0,cnt0=1 ; 6=110 -> cnt2=1,cnt1=1,cnt0=0
    # So count>=5 iff cnt2=1 AND (cnt0 OR cnt1). count<=4 iff NOT that = cnt2=0 OR (cnt2=1 AND cnt1=0 AND cnt0=0)... but max is 6 so cnt2=1 with 4? no. Values with cnt2=1: 4(100),5(101),6(110),7(111 impossible). 4 is allowed! 4=100 -> cnt2=1,cnt1=0,cnt0=0.
    # So among cnt2=1: allowed only 4 (cnt1=0,cnt0=0); disallowed 5,6.
    # count<=4 condition: (cnt2=0) OR (cnt2=1 AND cnt1=0 AND cnt0=0).
    # Equivalent forbidden(count>=5) = cnt2=1 AND (cnt1=1 OR cnt0=1).
    # We want phase -1 when: all_edges AND count<=4.
    # Use compute of a "bad" flag then phase = apply Z-like via multi-controlled.
    #
    # Strategy: build predicate P = all_edges AND NOT(cnt2 AND (cnt0 OR cnt1)).
    # Compute helper into cnt? no free ancilla. Instead use controlled-phase construction:
    # Apply phase -1 on states satisfying all_edges AND count<=4.
    # count<=4 = NOT forbidden. Write as sum of two disjoint mutually-exclusive terms:
    #   T_A: all_edges AND cnt2=0
    #   T_B: all_edges AND cnt2=1 AND cnt1=0 AND cnt0=0
    # These are disjoint; total phase = phase(T_A)+phase(T_B). Apply -1 to each.

    controls_all_edges = list(edge_anc)

    # T_A: all edges =1 and cnt2=0  -> multi-controlled-Z with cnt2 negated
    qc.x(cnt[2])
    qc.h(cnt[2])
    qc.mcx(controls_all_edges + [cnt[0]] if False else controls_all_edges + [], cnt[2]) if False else None
    # multi-controlled X onto cnt2 (used as phase target via H-sandwich) controlled by all edges + cnt2-was-0
    qc.mcx(controls_all_edges, cnt[2])
    qc.h(cnt[2])
    qc.x(cnt[2])

    # T_B: all edges=1 and cnt2=1 and cnt1=0 and cnt0=0
    qc.x(cnt[0]); qc.x(cnt[1])
    qc.h(cnt[0])
    qc.mcx(controls_all_edges + [cnt[2], cnt[1]], cnt[0])
    qc.h(cnt[0])
    qc.x(cnt[0]); qc.x(cnt[1])

    # ----- UNCOMPUTE -----
    uncompute_counter()
    uncompute_edges()
