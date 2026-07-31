from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Free cells: (2,1) = free cell 0, (2,2) = free cell 1.
    # Cell j: b0 = problem_qubits[2j], b1 = problem_qubits[2j+1], code c = b0 + 2*b1.
    # Decode surjective: 00->0, 01->1, 10->2, 11->0.
    # value == 0  iff code in {00, 11}  iff (b0 == b1)
    # value == 1  iff code == 01         iff (b0 & ~b1)
    # value == 2  iff code == 10         iff (~b0 & b1)
    #
    # Grid (rows 0..2), givens:
    #   row0: 0 2 1
    #   row1: 1 0 2
    #   row2: 2 F0 F1     where F0 at (2,1), F1 at (2,2)
    #
    # Constraints for a valid Latin square. Column and row analysis:
    #   row2 has given 2 at col0, plus F0, F1 -> row2 must be {0,1,2}
    #         so {F0,F1} = {0,1}.
    #   col1 givens: row0=2, row1=0, plus F0 -> col1 needs {0,1,2}
    #         so F0 must be 1.
    #   col2 givens: row0=1, row1=2, plus F1 -> col2 needs {0,1,2}
    #         so F1 must be 0.
    # Unique solution: F0 == 1  AND  F1 == 0.
    #
    # F0 == 1 : cell0 code == 01 -> b0=problem_qubits[0]=1, b1=problem_qubits[1]=0
    # F1 == 0 : cell1 value 0 -> code in {00,11} -> b0==b1
    #           b0=problem_qubits[2], b1=problem_qubits[3]

    p = problem_qubits
    a = ancilla_qubits

    # anc0 = 1 iff F0 == 1  (b0==1 and b1==0)
    # Compute: want anc0 = p[0] AND (NOT p[1]).
    qc.x(p[1])
    qc.ccx(p[0], p[1], a[0])
    qc.x(p[1])

    # anc1 = 1 iff F1 == 0  (b0 == b1), i.e. NOT(b0 XOR b1)
    qc.cx(p[2], a[1])
    qc.cx(p[3], a[1])
    qc.x(a[1])   # a[1] = NOT(b0 xor b1) = (b0==b1)

    # Phase -1 iff anc0 AND anc1
    qc.cz(a[0], a[1])

    # Uncompute anc1
    qc.x(a[1])
    qc.cx(p[3], a[1])
    qc.cx(p[2], a[1])

    # Uncompute anc0
    qc.x(p[1])
    qc.ccx(p[0], p[1], a[0])
    qc.x(p[1])
