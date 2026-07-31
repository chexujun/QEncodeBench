from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits, ancilla_qubits):
    # Free cells (row,col): 0->(0,0), 1->(0,1), 2->(1,2)
    # Grid givens:
    #   row0: (0,0)=A, (0,1)=B, (0,2)=1
    #   row1: (1,0)=2, (1,1)=1, (1,2)=C
    #   row2: (1,0)=1, (2,1)=0, (2,2)=2
    # Free vars: A=cell0, B=cell1, C=cell2
    # code bits: cell j -> b0=problem_qubits[2j], b1=problem_qubits[2j+1]
    # decode: 00->0,01->1,10->2,11->0
    # value == v iff code in set:
    #   v0: codes 00 or 11  -> (b0==b1)
    #   v1: code 01          -> (b0=1,b1=0)
    #   v2: code 10          -> (b0=0,b1=1)
    #
    # Latin constraints, deduce forced values:
    # Row0: A,B,1 distinct -> {A,B}={0,2}
    # Col0: A,2,1 distinct -> A in {0}  (not 2,not1) -> A must be 0
    # Then B=2. Check row0 {0,2,1} ok. Col1: B,1,0 -> {2,1,0} ok.
    # Col2: 1,C,2 distinct -> C=0. Row1: 2,1,C={2,1,0} ok.
    # So unique solution: A=0, B=2, C=0.
    # f(x)=1 iff decode(cell0)=0 AND decode(cell1)=2 AND decode(cell2)=0.

    b0_0, b1_0 = problem_qubits[0], problem_qubits[1]  # cell0 -> value 0
    b0_1, b1_1 = problem_qubits[2], problem_qubits[3]  # cell1 -> value 2
    b0_2, b1_2 = problem_qubits[4], problem_qubits[5]  # cell2 -> value 0

    a = ancilla_qubits

    # ---- compute predicates into ancillas ----
    # cell0 == value0  <=>  b0==b1  <=> NOT(b0 XOR b1)
    qc.cx(b0_0, a[0])
    qc.cx(b1_0, a[0])
    qc.x(a[0])            # a[0]=1 iff cell0 decodes to 0

    # cell1 == value2  <=>  b0=0, b1=1
    qc.x(b0_1)
    qc.ccx(b0_1, b1_1, a[1])   # a[1]=1 iff b0=0 and b1=1
    qc.x(b0_1)

    # cell2 == value0  <=>  b0==b1
    qc.cx(b0_2, a[2])
    qc.cx(b1_2, a[2])
    qc.x(a[2])            # a[2]=1 iff cell2 decodes to 0

    # ---- phase: -1 iff all three satisfied ----
    qc.h(a[3])
    qc.x(a[3])
    qc.mcx([a[0], a[1], a[2]], a[3])
    qc.x(a[3])
    qc.h(a[3])
    # (a[3] returns to |0>: it was |0>, H,X,...,X,H with controlled-X gives
    #  phase kickback -1 on the marked state, ancilla restored)

    # ---- uncompute predicates ----
    qc.x(a[2])
    qc.cx(b1_2, a[2])
    qc.cx(b0_2, a[2])

    qc.x(b0_1)
    qc.ccx(b0_1, b1_1, a[1])
    qc.x(b0_1)

    qc.x(a[0])
    qc.cx(b1_0, a[0])
    qc.cx(b0_0, a[0])
