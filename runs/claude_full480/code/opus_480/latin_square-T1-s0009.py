from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Free cells: j=0 -> (row0,col0), j=1 -> (row2,col1)
    # Cell j uses qubits problem_qubits[2j] (b0) and problem_qubits[2j+1] (b1)
    # Decoding: 00->0, 01->1, 10->2, 11->0
    #
    # Grid (given):
    #   row0: [X, 0, 2]   X = cell0
    #   row1: [0, 2, 1]
    #   row2: [2, Y, 0]   Y = cell1
    #
    # For a valid Latin square:
    #   row0 has 0 and 2 given -> X must be 1
    #   col0 has 0(row1),2(row2) given -> X must be 1  (consistent)
    #   row2 has 2 and 0 given -> Y must be 1
    #   col1 has 0(row0),2(row1) given -> Y must be 1  (consistent)
    # So f(x)=1 iff cell0 decodes to 1 AND cell1 decodes to 1.
    # value==1 iff code==01 iff b0==1 and b1==0.

    c0_b0 = problem_qubits[0]
    c0_b1 = problem_qubits[1]
    c1_b0 = problem_qubits[2]
    c1_b1 = problem_qubits[3]

    # predicate = (c0_b0=1 AND c0_b1=0) AND (c1_b0=1 AND c1_b1=0)
    # Flip the b1 bits so that all-ones corresponds to the target,
    # use an mcx over [c0_b0, ~c0_b1, c1_b0, ~c1_b1].
    a = ancilla_qubits[0]

    qc.x(c0_b1)
    qc.x(c1_b1)

    qc.mcx([c0_b0, c0_b1, c1_b0, c1_b1], a)
    qc.z(a)
    qc.mcx([c0_b0, c0_b1, c1_b0, c1_b1], a)

    qc.x(c0_b1)
    qc.x(c1_b1)
