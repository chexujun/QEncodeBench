import numpy as np
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 1), (0, 3), (0, 4), (1, 3), (1, 4), (2, 3)]
    k = 3
    n = len(problem_qubits)

    # ---- ancilla layout ----
    # 6 edge ancillas: one per edge, set to 1 iff edge is covered
    edge_anc = ancilla_qubits[0:6]
    # 2 count ancillas: 2-bit counter of number of "uncovered" edges? No -> we need popcount of x <= 3.
    # Reuse remaining 3 ancillas: 2 for popcount register (max count 5 needs 3 bits), 1 as final flag.
    # We have 9 ancillas total: 6 edge + 3 remaining.
    cnt = ancilla_qubits[6:9]  # 3-bit counter for popcount of the 5 problem bits (0..5)
    # But we also need a flag; reuse edge ancillas after they are consumed? Must keep edge results
    # until final AND. Instead: compute size-constraint into a marker using the count register, then
    # combine. We need one more qubit for the final AND flag -> use one edge ancilla temporarily? No.
    # Strategy: compute everything into edge_anc(6) as "edge covered" bits (all must be 1).
    # Compute popcount into cnt(3). Predicate size<=3 == NOT(count>=4) == NOT(cnt bit pattern >=4).
    # count in {0..5}; count>=4 iff cnt2==1 AND (cnt1==1 OR cnt0==1). We can flip edge-cover logic:
    # We want mark iff (all 6 edges covered) AND (count<=3).
    # Represent "size ok" by temporarily setting one edge ancilla? We must not clobber. Instead we
    # apply the multi-controlled phase directly on: 6 edge_anc (control=1) AND size-ok condition.
    # size-ok = NOT(count>=4). Express count>=4 detection via cnt bits without extra ancilla by
    # controlling the final MCP on cnt bits with appropriate polarity. But MCP needs a single AND.
    # We AND: edge0..5 ==1, and (count<=3). count<=3 == NOT(cnt2 AND (cnt1 OR cnt0)).
    # Hard to fold OR into one MCP. So enumerate the two "bad-size" patterns count=4 (100? ) —
    # in binary count: 4=100, 5=101. Both have cnt2=1. count in 0..5; cnt2=1 exactly for 4,5.
    # So count<=3  <=>  cnt2==0 !  (since 6,7 impossible with only 5 bits max popcount 5).
    # Great: size-ok simply = (cnt2 == 0).

    # ---- compute edge-covered bits ----
    for idx, (u, v) in enumerate(edges):
        a = edge_anc[idx]
        # covered = qu OR qv = NOT( (NOT qu) AND (NOT qv) )
        qu, qv = problem_qubits[u], problem_qubits[v]
        qc.x(qu)
        qc.x(qv)
        qc.ccx(qu, qv, a)   # a = (NOT qu)(NOT qv) computed with inverted inputs -> a = AND of negations
        qc.x(qu)
        qc.x(qv)
        qc.x(a)             # a = OR(qu,qv) = covered

    # ---- popcount of problem bits into 3-bit counter cnt (ripple add of single bits) ----
    # cnt initially 0. Add each problem bit.
    c0, c1, c2 = cnt[0], cnt[1], cnt[2]
    for i in range(n):
        b = problem_qubits[i]
        # add b into 3-bit counter: carry chain
        # new c2 ^= c1 & c0 & b  (carry from bit1)
        qc.mcx([b, c0, c1], c2)
        # new c1 ^= c0 & b
        qc.ccx(b, c0, c1)
        # new c0 ^= b
        qc.cx(b, c0)

    # ---- phase: -1 iff all edge_anc==1 AND cnt2==0 ----
    # controls: edge_anc all =1, cnt2 =0 (open control -> X wrap)
    qc.x(c2)
    ctrls = list(edge_anc) + [c2]
    qc.h(ctrls[-1])
    qc.mcx(ctrls[:-1], ctrls[-1])
    qc.h(ctrls[-1])
    qc.x(c2)

    # ---- uncompute popcount (reverse order) ----
    for i in reversed(range(n)):
        b = problem_qubits[i]
        qc.cx(b, c0)
        qc.ccx(b, c0, c1)
        qc.mcx([b, c0, c1], c2)

    # ---- uncompute edge-covered bits (reverse) ----
    for idx, (u, v) in enumerate(reversed(edges)):
        a = edge_anc[len(edges) - 1 - idx]
        qu, qv = problem_qubits[u], problem_qubits[v]
        qc.x(a)
        qc.x(qu)
        qc.x(qv)
        qc.ccx(qu, qv, a)
        qc.x(qu)
        qc.x(qv)
