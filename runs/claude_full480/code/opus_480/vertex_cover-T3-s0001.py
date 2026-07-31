import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 3), (1, 2), (2, 3), (2, 4), (2, 5), (3, 4)]
    n = 6
    p = problem_qubits

    # ancilla layout
    edge_anc = ancilla_qubits[0:6]      # one per edge: 1 iff edge covered
    cnt_anc = ancilla_qubits[6:9]       # 3-bit popcount register (max count 6 -> 3 bits)
    # We need to check popcount <= 2, i.e. NOT (popcount >= 3).
    # Use edge flags AND (popcount<=2) into a final marker; but we only have 9 ancillas.
    # Reuse: after computing edges into edge_anc (6) we still need count + predicate.
    # Instead of storing all 6 edge flags simultaneously with a separate count register,
    # compute the full predicate onto edge_anc[0] via a chain, but that needs many ancillas.
    #
    # Strategy: compute popcount into cnt_anc (3 qubits), compute all-edges-covered into
    # one flag, AND them, phase, uncompute.

    c0, c1, c2 = cnt_anc  # binary counter bits (LSB c0)

    def add_one(ctrl):
        # controlled increment of 3-bit counter (c2 c1 c0) by 1, controlled on ctrl
        # carry chain: increment
        qc.ccx(ctrl, c1, c2)
        qc.ccx(ctrl, c0, c1)
        qc.cx(ctrl, c0)

    def add_one_inv(ctrl):
        qc.cx(ctrl, c0)
        qc.ccx(ctrl, c0, c1)
        qc.ccx(ctrl, c1, c2)

    def compute():
        # popcount of the 6 problem qubits
        for i in range(n):
            add_one(p[i])
        # edge flags: edge covered iff (x_u OR x_v). Compute into edge_anc via De Morgan:
        # covered = NOT(NOT x_u AND NOT x_v).  Set edge flag = 1 if covered.
        for idx, (u, v) in enumerate(edges):
            a = edge_anc[idx]
            qc.x(p[u]); qc.x(p[v])
            qc.ccx(p[u], p[v], a)   # a = (not x_u)&(not x_v) = edge NOT covered
            qc.x(p[u]); qc.x(p[v])
            qc.x(a)                 # a = edge covered

    def uncompute():
        for idx, (u, v) in reversed(list(enumerate(edges))):
            a = edge_anc[idx]
            qc.x(a)
            qc.x(p[u]); qc.x(p[v])
            qc.ccx(p[u], p[v], a)
            qc.x(p[u]); qc.x(p[v])
        for i in reversed(range(n)):
            add_one_inv(p[i])

    compute()

    # predicate: all six edge flags == 1  AND  popcount <= 2 (i.e. c2==0 and not(c1==1 and c0==1))
    # popcount<=2 means count in {0,1,2}: c2 must be 0, and (c1,c0) != (1,1).
    # Condition count<=2  <=>  NOT c2  AND  NOT(c1 AND c0).
    # We'll place a phase (-1) on states satisfying full predicate using a multi-controlled Z.
    # Build controls: all edge flags =1, c2=0, and (c1 & c0)!=1.
    # Handle the (c1,c0)!=(1,1) by splitting into the two allowed high-bit patterns:
    #   count<=2 with c2=0 valid (c1,c0) in {00,01,10}. Equivalent: NOT(c1 AND c0).
    # Use an auxiliary: flip phase for "all edges & c2=0" then subtract "all edges & c2=0 & c1 & c0".

    # Phase for A = (all edges) AND (c2==0):
    ctrls_all = list(edge_anc)
    qc.x(c2)
    # multi-controlled Z on ctrls_all + c2 (now c2 flipped so control on original 0)
    qc.h(edge_anc[0])
    qc.mcx(ctrls_all[1:] + [c2], edge_anc[0])
    qc.h(edge_anc[0])
    qc.x(c2)

    # Undo the overcount: states with all edges & c2==0 & c1==1 & c0==1 (count==3) got -1
    # but should be +1 (unchanged) -> apply another -1 to flip them back.
    qc.x(c2)
    qc.h(edge_anc[0])
    qc.mcx(ctrls_all[1:] + [c2, c1, c0], edge_anc[0])
    qc.h(edge_anc[0])
    qc.x(c2)

    uncompute()
