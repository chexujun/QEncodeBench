from qiskit import QuantumCircuit
from math import pi


def build_oracle(qc: QuantumCircuit, problem_qubits, ancilla_qubits):
    p = problem_qubits
    edges = [(0, 2), (0, 4), (1, 4), (2, 4), (3, 4)]

    # ancilla layout
    edge_anc = ancilla_qubits[0:5]   # one ancilla per edge (edge covered flag)
    cnt = ancilla_qubits[5:8]        # 3-bit popcount register (counts up to 5)
    flag = ancilla_qubits[7]         # reuse: actually need separate; use index 7? we used 5,6,7 for cnt
    # We only have 8 ancillas: 5 edges + 3 count = 8. Need a final flag too.
    # Reallocate: reuse edge ancillas region after uncompute is not possible mid-phase.
    # Instead: compute all-edges-covered into edge_anc via mcx into one, and count into cnt.

    # ---- compute edge-covered flags: edge_anc[i] = OR(x_u, x_v) ----
    for i, (u, v) in enumerate(edges):
        a = edge_anc[i]
        qc.x(p[u]); qc.x(p[v])
        qc.x(a)
        qc.ccx(p[u], p[v], a)   # a = 1 - (~xu & ~xv) = OR
        qc.x(p[u]); qc.x(p[v])

    # ---- compute popcount of x into cnt (3 bits) via ripple increment ----
    # increment cnt by each problem bit, controlled
    for i in range(5):
        ctrl = p[i]
        # ripple carry increment: cnt += ctrl
        # bit2 ^= ctrl & cnt0 & cnt1
        qc.mcx([ctrl, cnt[0], cnt[1]], cnt[2])
        qc.ccx(ctrl, cnt[0], cnt[1])
        qc.cx(ctrl, cnt[0])

    # size <= 2  <=>  NOT(count >= 3). count in {0..5}. count>=3 means (cnt2 set) or (cnt1 & cnt0).
    # We want condition size<=2: cnt2==0 AND NOT(cnt1&cnt0).
    # Build predicate: all edges covered AND size<=2, phase onto it.
    # Use multi-controlled Z with controls: all edge_anc ==1, cnt2==0, and (cnt1&cnt0)==0.
    # Handle the "not(cnt1 and cnt0)" by an auxiliary: we lack a free ancilla, so use cnt-based trick.
    # count in 0..5 with size<=2 means count in {0,1,2}: binary 000,001,010. cnt2=0 and cnt1,cnt0 not both 1.
    # Enumerate valid count patterns {000,001,010}: mark via controlled phase for each with edges.

    controls = edge_anc[:]  # all must be 1
    # For each allowed count value, flip its zero-bits to ones, MCZ, flip back.
    allowed = [0, 1, 2]
    for val in allowed:
        b0 = val & 1
        b1 = (val >> 1) & 1
        b2 = (val >> 2) & 1
        flips = []
        for bit, cq in zip((b0, b1, b2), cnt):
            if bit == 0:
                qc.x(cq); flips.append(cq)
        allc = controls + list(cnt)
        qc.h(allc[-1])
        qc.mcx(allc[:-1], allc[-1])
        qc.h(allc[-1])
        for cq in flips:
            qc.x(cq)

    # ---- uncompute popcount ----
    for i in reversed(range(5)):
        ctrl = p[i]
        qc.cx(ctrl, cnt[0])
        qc.ccx(ctrl, cnt[0], cnt[1])
        qc.mcx([ctrl, cnt[0], cnt[1]], cnt[2])

    # ---- uncompute edge flags ----
    for i, (u, v) in enumerate(edges):
        a = edge_anc[i]
        qc.x(p[u]); qc.x(p[v])
        qc.ccx(p[u], p[v], a)
        qc.x(a)
        qc.x(p[u]); qc.x(p[v])
