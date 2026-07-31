from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    edges = [(0, 2), (1, 2), (1, 3), (2, 3)]

    edge_anc = ancilla_qubits[0:4]      # one ancilla per edge (edge covered flag)
    cnt = ancilla_qubits[4:7]           # 3-qubit counter of Hamming weight (values 0..4)

    q = problem_qubits

    # ---- compute: edge coverage ----
    # edge covered = OR of its two endpoints = NOT(AND(NOT a, NOT b))
    for idx, (u, v) in enumerate(edges):
        a = edge_anc[idx]
        qc.x(q[u]); qc.x(q[v])
        qc.ccx(q[u], q[v], a)   # a = 1 iff both endpoints are 0 (edge uncovered)
        qc.x(q[u]); qc.x(q[v])
        qc.x(a)                 # a = 1 iff edge covered

    # ---- compute: Hamming weight counter (cnt = number of 1-bits among x0..x3) ----
    # increment counter by each xi using a 3-bit ripple increment controlled on xi
    def controlled_increment(ctrl):
        # increment 3-bit counter cnt[0]=LSB when ctrl=1
        # carry chain: bit2 ^= ctrl & c0 & c1 ; bit1 ^= ctrl & c0 ; bit0 ^= ctrl
        qc.mcx([ctrl, cnt[0], cnt[1]], cnt[2])
        qc.ccx(ctrl, cnt[0], cnt[1])
        qc.cx(ctrl, cnt[0])

    for xi in [x0, x1, x2, x3]:
        controlled_increment(xi)

    # size <= 2 means counter value in {0,1,2} -> bit1..bit2 pattern: NOT(cnt>=3)
    # cnt>=3 iff cnt2==1 (values 4) or (cnt1==1 and cnt0==1) (value 3)
    # size_ok flag stored on... we fold it into the phase multi-control instead.

    # ---- phase ----
    # f=1 iff all 4 edge flags == 1 AND size<=2.
    # size<=2 <=> NOT(value>=3) <=> NOT( cnt2==1 OR (cnt1 AND cnt0) )
    # We build a size_ok ancilla by reusing edge_anc after... but all in use.
    # Instead: apply phase as MCP(pi) over controls {edge flags} conditioned on size_ok.
    # Compute size_bad into cnt is awkward; use the fact value in 0..4 with 3 bits.
    # value>=3 patterns: 011(3),100(4). Note 100 => cnt2=1. 011 => cnt2=0,cnt1=1,cnt0=1.
    # size_ok = NOT(cnt2) AND NOT(cnt1 AND cnt0)

    # Build combined multi-controlled Z:
    # We want phase -1 iff edge0..3 all 1, cnt2==0, and NOT(cnt1 & cnt0).
    # Split value>=3 into two disjoint cases and subtract? Simpler: enumerate size_ok
    # via two multi-controlled phases over the disjoint good size-values that also
    # require all edges covered.

    # Good sizes with all edges covered: use controls all-edges + specific cnt pattern.
    # Apply phase for each allowed counter value v in {0,1,2} (patterns of cnt bits):
    #   v=0 -> 000, v=1 -> 001, v=2 -> 010
    # For each, MCP(pi) over [edge0..3, cnt0,cnt1,cnt2] with X-conditioning on the
    # zero bits.
    allowed_patterns = {0: (0, 0, 0), 1: (1, 0, 0), 2: (0, 1, 0)}
    controls = edge_anc + cnt
    for v, (b0, b1, b2) in allowed_patterns.items():
        flips = []
        if b0 == 0: flips.append(cnt[0])
        if b1 == 0: flips.append(cnt[1])
        if b2 == 0: flips.append(cnt[2])
        for fq in flips:
            qc.x(fq)
        qc.h(controls[-1])
        qc.mcx(controls[:-1], controls[-1])
        qc.h(controls[-1])
        for fq in flips:
            qc.x(fq)

    # ---- uncompute counter ----
    for xi in [x3, x2, x1, x0]:
        qc.cx(xi, cnt[0])
        qc.ccx(xi, cnt[0], cnt[1])
        qc.mcx([xi, cnt[0], cnt[1]], cnt[2])

    # ---- uncompute edge coverage ----
    for idx, (u, v) in enumerate(edges):
        a = edge_anc[idx]
        qc.x(a)
        qc.x(q[u]); qc.x(q[v])
        qc.ccx(q[u], q[v], a)
        qc.x(q[u]); qc.x(q[v])
