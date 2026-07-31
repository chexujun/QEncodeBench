from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Free cells in order: (0,1)=cell0, (2,0)=cell1, (2,2)=cell2
    # Givens:
    #   row0: 1 . 2   -> row0 has {1,2}, free (0,1)=cell0 must be 0
    #   row1: 2 1 0   (fully given)
    #   row2: . 2 .   -> row2 has {2}, free (2,0)=cell1, (2,2)=cell2 -> must be {0,1}
    # Columns:
    #   col0: 1,2,cell1 -> given {1,2}, cell1 must be 0
    #   col1: cell0,1,2 -> given {1,2}, cell0 must be 0
    #   col2: 2,0,cell2 -> given {2,0}, cell2 must be 1
    # Unique solution: cell0=0, cell1=0, cell2=1
    # Decoding surjective: value0 <- codes 00 or 11 ; value1 <- code 01 ; value2 <- code 10
    #
    # Predicate f(x)=1 iff cell0==0 and cell1==0 and cell2==1.
    #   cellX==0  iff (b0,b1) in {00,11} iff b0==b1
    #   cellX==1  iff (b0,b1)==(1,0) iff b0==1 and b1==0

    c0b0, c0b1 = problem_qubits[0], problem_qubits[1]
    c1b0, c1b1 = problem_qubits[2], problem_qubits[3]
    c2b0, c2b1 = problem_qubits[4], problem_qubits[5]

    # Ancillas for per-cell predicates
    a0 = ancilla_qubits[0]  # cell0==0  : b0==b1
    a1 = ancilla_qubits[1]  # cell1==0  : b0==b1
    a2 = ancilla_qubits[2]  # cell2==1  : b0==1 and b1==0

    # Compute a0 = NOT(c0b0 XOR c0b1) = 1 iff equal
    qc.cx(c0b0, a0)
    qc.cx(c0b1, a0)
    qc.x(a0)

    # Compute a1 = 1 iff c1b0 == c1b1
    qc.cx(c1b0, a1)
    qc.cx(c1b1, a1)
    qc.x(a1)

    # Compute a2 = 1 iff c2b0==1 and c2b1==0
    qc.x(c2b1)
    qc.ccx(c2b0, c2b1, a2)
    qc.x(c2b1)

    # Phase: -1 iff a0 & a1 & a2
    qc.h(a2)
    qc.ccx(a0, a1, a2)
    qc.h(a2)

    # Uncompute a2
    qc.x(c2b1)
    qc.ccx(c2b0, c2b1, a2)
    qc.x(c2b1)

    # Uncompute a1
    qc.x(a1)
    qc.cx(c1b1, a1)
    qc.cx(c1b0, a1)

    # Uncompute a0
    qc.x(a0)
    qc.cx(c0b1, a0)
    qc.cx(c0b0, a0)
