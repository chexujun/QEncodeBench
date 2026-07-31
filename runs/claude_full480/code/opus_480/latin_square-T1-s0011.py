from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Free cells: j=0 -> (row0,col0), j=1 -> (row1,col2)
    # Cell j value bits: b0 = problem_qubits[2j], b1 = problem_qubits[2j+1]
    # Decode surjective: 00->0, 01->1, 10->2, 11->0
    # Grid givens:
    #   row0: [ .  0  2 ]
    #   row1: [ 2  1  . ]
    #   row2: [ 0  2  1 ]
    # Free cell 0 = (0,0). Row0 already has {0,2} -> must be 1 -> code must decode to 1 -> code==01
    #   Col0 already has {2,0} (rows1,2) -> must be 1 -> consistent: value 1.
    # Free cell 1 = (1,2). Row1 already has {2,1} -> must be 0 -> code decodes to 0 -> code 00 or 11
    #   Col2 already has {2,1} (rows0,2) -> must be 0 -> consistent.
    #
    # So predicate f = 1 iff:
    #   cell0 decodes to 1  => (b0=1, b1=0) i.e. code == 01
    #   cell1 decodes to 0  => code == 00 or 11 => (b0 == b1)
    #
    # cell0 qubits:
    c0b0 = problem_qubits[0]
    c0b1 = problem_qubits[1]
    # cell1 qubits:
    c1b0 = problem_qubits[2]
    c1b1 = problem_qubits[3]

    # Predicate A (cell0 == 01): c0b0 == 1 AND c0b1 == 0
    # Predicate B (cell1 in {00,11}): c1b0 == c1b1  (b0 XNOR b1)
    #
    # f = A AND B. Compute into ancilla, phase, uncompute.

    a_A = ancilla_qubits[0]   # holds A = c0b0 & ~c0b1
    a_B = ancilla_qubits[1]   # holds B = ~(c0b0 xor c0b1) for cell1
    a_f = ancilla_qubits[2]   # holds A & B

    # Compute A = c0b0 AND (NOT c0b1)
    qc.x(c0b1)
    qc.ccx(c0b0, c0b1, a_A)
    qc.x(c0b1)

    # Compute B = NOT(c1b0 XOR c1b1): put XOR into a_B then flip
    qc.cx(c1b0, a_B)
    qc.cx(c1b1, a_B)
    qc.x(a_B)   # a_B = 1 iff c1b0 == c1b1

    # f = A AND B
    qc.ccx(a_A, a_B, a_f)

    # Phase
    qc.z(a_f)

    # Uncompute (mirror)
    qc.ccx(a_A, a_B, a_f)

    qc.x(a_B)
    qc.cx(c1b1, a_B)
    qc.cx(c1b0, a_B)

    qc.x(c0b1)
    qc.ccx(c0b0, c0b1, a_A)
    qc.x(c0b1)
