from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Free cells in order: fc0 = (row1,col2), fc1 = (row2,col0)
    # Grid givens:
    #   row0: 2 0 1
    #   row1: 1 2 fc0
    #   row2: fc1 1 2
    # Column givens:
    #   col0: 2 1 fc1
    #   col1: 0 2 1
    #   col2: 1 fc0 2
    #
    # Codes (2 qubits each), surjective decode: 00->0, 01->1, 10->2, 11->0.
    # fc0 low bit = problem_qubits[0], high = problem_qubits[1]
    # fc1 low bit = problem_qubits[2], high = problem_qubits[3]
    #
    # Constraints that involve free cells:
    #   row1 = {1, 2, fc0}  -> fc0 must be 0
    #   col2 = {1, 2, fc0}  -> fc0 must be 0
    #   row2 = {fc1, 1, 2}  -> fc1 must be 0
    #   col0 = {2, 1, fc1}  -> fc1 must be 0
    # All other rows/cols are already complete and valid.
    #
    # So f(x) = 1 iff decode(fc0) == 0 AND decode(fc1) == 0.
    # decode == 0 iff code in {00, 11} iff (b0 == b1).
    # For a pair (b0,b1): equal iff b0 XNOR b1 == 1.

    f0_lo, f0_hi = problem_qubits[0], problem_qubits[1]
    f1_lo, f1_hi = problem_qubits[2], problem_qubits[3]

    a0 = ancilla_qubits[0]  # will hold (fc0 equal) = XNOR(b0,b1)
    a1 = ancilla_qubits[1]  # will hold (fc1 equal)

    # Compute a0 = XNOR(f0_lo, f0_hi):  a0 = 1 xor f0_lo xor f0_hi
    qc.x(a0)
    qc.cx(f0_lo, a0)
    qc.cx(f0_hi, a0)

    # Compute a1 = XNOR(f1_lo, f1_hi)
    qc.x(a1)
    qc.cx(f1_lo, a1)
    qc.cx(f1_hi, a1)

    # Phase -1 iff a0 == 1 AND a1 == 1
    qc.cz(a0, a1)

    # Uncompute a1
    qc.cx(f1_hi, a1)
    qc.cx(f1_lo, a1)
    qc.x(a1)

    # Uncompute a0
    qc.cx(f0_hi, a0)
    qc.cx(f0_lo, a0)
    qc.x(a0)
