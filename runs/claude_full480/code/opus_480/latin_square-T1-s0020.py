import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Free cells: A=(0,2), B=(2,1). Each has code (b0,b1), value = 0,1,2, or 0 (for 11).
    # Grid givens:
    #   row0: 2 1 A      row1: 0 2 1      row2: 1 B 2
    #   col0: 2 0 1      col1: 1 2 B      col2: A 1 2
    # Row0 already has {2,1}; free A in row0 -> A must be 0.
    # Col2 already has {1,2}; free A in col2 -> A must be 0.
    # Row2 already has {1,2}; free B in row2 -> B must be 0.
    # Col1 already has {1,2}; free B in col1 -> B must be 0.
    # So valid iff value(A)==0 AND value(B)==0.
    # value==0 iff code in {00, 11} i.e. b0 == b1.
    # value(A)==0: A_b0 == A_b1 ; value(B)==0: B_b0 == B_b1.
    aA0, aA1 = problem_qubits[0], problem_qubits[1]
    aB0, aB1 = problem_qubits[2], problem_qubits[3]

    eqA = ancilla_qubits[0]  # 1 iff A_b0 == A_b1
    eqB = ancilla_qubits[1]  # 1 iff B_b0 == B_b1

    # eqA = NOT(A_b0 XOR A_b1)
    qc.cx(aA0, eqA)
    qc.cx(aA1, eqA)
    qc.x(eqA)

    # eqB = NOT(B_b0 XOR B_b1)
    qc.cx(aB0, eqB)
    qc.cx(aB1, eqB)
    qc.x(eqB)

    # phase -1 iff eqA AND eqB
    qc.cz(eqA, eqB)

    # uncompute
    qc.x(eqB)
    qc.cx(aB1, eqB)
    qc.cx(aB0, eqB)

    qc.x(eqA)
    qc.cx(aA1, eqA)
    qc.cx(aA0, eqA)
