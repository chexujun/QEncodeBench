from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Free cells: (0,2) -> cell0, (2,1) -> cell1
    # cell0 code from problem_qubits[0](b0), problem_qubits[1](b1)
    # cell1 code from problem_qubits[2](b0), problem_qubits[3](b1)
    #
    # Grid:
    #   1 2 A      A = cell0 at (0,2)
    #   0 1 2
    #   2 B 1      B = cell1 at (2,1)
    #
    # Row0 has {1,2}, needs A = 0.
    # Col2 has {A, 2, 1}: needs A = 0 -> consistent.
    # Row2 has {2, B, 1}, needs B = 0.
    # Col1 has {2, 1, B}: needs B = 0 -> consistent.
    #
    # Decoding (surjective): code 00->0, 01->1, 10->2, 11->0.
    # value 0 iff code in {00, 11}, i.e. b0 == b1.
    #
    # So predicate: (A decodes to 0) AND (B decodes to 0)
    #   = (a0 == a1) AND (b0 == b1)
    #   = NOT(a0 xor a1) AND NOT(b0 xor b1)

    a0 = problem_qubits[0]
    a1 = problem_qubits[1]
    b0 = problem_qubits[2]
    b1 = problem_qubits[3]

    anc_a = ancilla_qubits[0]   # will hold (a0 xor a1)
    anc_b = ancilla_qubits[1]   # will hold (b0 xor b1)

    # compute parity of cell0 into anc_a
    qc.cx(a0, anc_a)
    qc.cx(a1, anc_a)
    # compute parity of cell1 into anc_b
    qc.cx(b0, anc_b)
    qc.cx(b1, anc_b)

    # We want phase -1 iff anc_a == 0 AND anc_b == 0.
    # Flip both so that the condition becomes both == 1, then CZ.
    qc.x(anc_a)
    qc.x(anc_b)

    # phase -1 iff anc_a == 1 and anc_b == 1
    qc.cz(anc_a, anc_b)

    # undo flips
    qc.x(anc_b)
    qc.x(anc_a)

    # uncompute parities (mirror)
    qc.cx(b1, anc_b)
    qc.cx(b0, anc_b)
    qc.cx(a1, anc_a)
    qc.cx(a0, anc_a)
