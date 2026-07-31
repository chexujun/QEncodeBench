from qiskit import QuantumCircuit
from math import pi


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Free cells (row,col): 0:(0,0) 1:(1,0) 2:(1,2) 3:(2,1)
    # Grid givens:
    #   row0: . 1 2      row1: . 2 .      row2: 2 . 1
    # Free cell code c (2 qubits): 00->0 01->1 10->2 11->0
    # A free cell "is value v" via its two qubits (b0 low, b1 high):
    #   value0: (b0,b1) in {00,11}
    #   value1: 01
    #   value2: 10
    #
    # Constraints that must ALL hold for a valid Latin square:
    #  Row0: cells {given1,given2, free0}. free0 must be 0.
    #  Row1: {free1, given2, free2}. free1 and free2 from {0,1}, distinct -> {0,1}.
    #  Row2: {given2, free3, given1}. free3 must be 0.
    #  Col0: {free0, free1, given2}. free0,free1 from {0,1}, distinct.
    #  Col1: {given1, given2, free3}. free3 must be 0. (consistent)
    #  Col2: {given2, free2, given1}. free2 must be 0.
    #
    # Solve: free0=0, free3=0, free2=0. Row1 distinct -> free1=1. Col0 distinct ok.
    # Unique solution: free0=0, free1=1, free2=0, free3=0.
    # Predicate f = [free0==0] AND [free1==1] AND [free2==0] AND [free3==0].
    #
    # value0 predicate on (b0,b1): NOT(b0 XOR b1)  i.e. b0==b1
    # value1 predicate on (b0,b1): b0 AND NOT b1

    def qb(j):  # (low, high) qubits of free cell j
        return problem_qubits[2 * j], problem_qubits[2 * j + 1]

    b00, b01 = qb(0)   # free0
    b10, b11 = qb(1)   # free1
    b20, b21 = qb(2)   # free2
    b30, b31 = qb(3)   # free3

    anc = ancilla_qubits  # 6 available; use 4 predicate + 1 combine

    # ---- compute per-cell predicates into ancillas ----
    # free0 == 0  <=> b00 == b01  -> anc[0]
    qc.cx(b00, b01)
    qc.x(b01)
    qc.cx(b01, anc[0])
    qc.x(b01)
    qc.cx(b00, b01)  # restore b01

    # free1 == 1  <=> b10==1 and b11==0 -> anc[1]
    qc.x(b11)
    qc.ccx(b10, b11, anc[1])
    qc.x(b11)

    # free2 == 0 <=> b20 == b21 -> anc[2]
    qc.cx(b20, b21)
    qc.x(b21)
    qc.cx(b21, anc[2])
    qc.x(b21)
    qc.cx(b20, b21)

    # free3 == 0 <=> b30 == b31 -> anc[3]
    qc.cx(b30, b31)
    qc.x(b31)
    qc.cx(b31, anc[3])
    qc.x(b31)
    qc.cx(b30, b31)

    # ---- phase if all four predicates true ----
    qc.h(anc[4])
    qc.mcx([anc[0], anc[1], anc[2], anc[3]], anc[4])
    qc.h(anc[4])

    # ---- uncompute predicates (mirror) ----
    qc.cx(b30, b31)
    qc.x(b31)
    qc.cx(b31, anc[3])
    qc.x(b31)
    qc.cx(b30, b31)

    qc.cx(b20, b21)
    qc.x(b21)
    qc.cx(b21, anc[2])
    qc.x(b21)
    qc.cx(b20, b21)

    qc.x(b11)
    qc.ccx(b10, b11, anc[1])
    qc.x(b11)

    qc.cx(b00, b01)
    qc.x(b01)
    qc.cx(b01, anc[0])
    qc.x(b01)
    qc.cx(b00, b01)
