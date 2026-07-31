from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Grid (rows). Givens use fixed values; free cells decoded from qubits.
    # Free cells in order: (0,0)=cell0, (1,2)=cell1, (2,0)=cell2.
    # Codes: 00->0, 01->1, 10->2, 11->0. bit0=problem_qubits[2j], bit1=problem_qubits[2j+1].
    #
    # Grid layout with variables:
    #   row0: A   2   1
    #   row1: 1   0   B
    #   row2: C   1   0
    #
    # Latin square constraints (each row/col a permutation of {0,1,2}).
    # Givens already: row0 has {2,1}, so A must be 0.
    # row1 has {1,0}, so B must be 2.
    # row2 has {1,0}, so C must be 2.
    # col0 has A(row0),1(row1),C(row2): needs {0,1,2} -> A,C in {0,2}, with 1 given. A!=C.
    # col2 has 1(row0),B(row1),0(row2): needs {0,1,2} -> B must be 2. consistent.
    # So unique solution: A=0, B=2, C=2.
    #
    # Predicate f(x)=1 iff decode(cell0)=0 AND decode(cell1)=2 AND decode(cell2)=2.
    #
    # decode==0 : codes 00 or 11  => b0==b1
    # decode==2 : code 10         => b0==0 and b1==1

    a0, a1, a2 = problem_qubits[0], problem_qubits[1]  # cell0 bits b0,b1
    b0, b1 = problem_qubits[2], problem_qubits[3]      # cell1 bits
    c0, c1 = problem_qubits[4], problem_qubits[5]      # cell2 bits

    p0 = ancilla_qubits[0]  # cell0 == 0  (b0 == b1)
    p1 = ancilla_qubits[1]  # cell1 == 2  (b0==0, b1==1)
    p2 = ancilla_qubits[2]  # cell2 == 2  (b0==0, b1==1)

    # ---- compute predicate flags ----
    # cell0 == 0  <=>  a0 XOR a1 == 0.  Set p0 = NOT(a0 xor a1).
    qc.cx(a0, p0)
    qc.cx(a1, p0)
    qc.x(p0)   # p0 = 1 iff a0==a1  (decode==0)

    # cell1 == 2  <=>  b0==0 and b1==1.  p1 = (NOT b0) AND b1.
    qc.x(b0)
    qc.ccx(b0, b1, p1)
    qc.x(b0)

    # cell2 == 2  <=>  c0==0 and c1==1.  p2 = (NOT c0) AND c1.
    qc.x(c0)
    qc.ccx(c0, c1, p2)
    qc.x(c0)

    # ---- phase: -1 iff p0 & p1 & p2 ----
    qc.h(p2)
    qc.ccx(p0, p1, p2)
    qc.h(p2)

    # ---- uncompute (mirror) ----
    qc.x(c0)
    qc.ccx(c0, c1, p2)
    qc.x(c0)

    qc.x(b0)
    qc.ccx(b0, b1, p1)
    qc.x(b0)

    qc.x(p0)
    qc.cx(a1, p0)
    qc.cx(a0, p0)
