from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Grid layout (rows top to bottom), givens:
    #   r0: [ ., 2, 0 ]
    #   r1: [ ., 0, . ]
    #   r2: [ 0, 1, 2 ]
    # Free cells in order: (0,0)=A, (1,0)=B, (1,2)=C
    # Cell code (2 qubits): b0 low = problem_qubits[2j], b1 high = problem_qubits[2j+1]
    # Decoding surjective: 00->0, 01->1, 10->2, 11->0
    # So decoded value: v==0 iff (b0,b1) in {00,11}; v==1 iff 01; v==2 iff 10.

    A0, A1 = problem_qubits[0], problem_qubits[1]
    B0, B1 = problem_qubits[2], problem_qubits[3]
    C0, C1 = problem_qubits[4], problem_qubits[5]

    # Constraints to satisfy for a valid Latin square:
    # Row0: [A, 2, 0]  -> A must be 1  (row already has 2 and 0)
    # Row1: [B, 0, C]  -> {B,C} must be {1,2} and both != 0
    # Row2 fixed valid.
    # Col0: [A, B, 0]  -> {A,B} must be {1,2}
    # Col1: [2, 0, 1]  fixed valid.
    # Col2: [0, C, 2]  -> C must be 1
    #
    # Combine: A==1 (from row0). C==1 (from col2).
    # Col0: {A,B}={1,2} with A==1 -> B==2.
    # Row1: {B,C}={1,2} with C==1 -> B==2. Consistent.
    # Therefore the unique solution: A==1, B==2, C==1.
    #
    # Decoded-value predicates on codes:
    #   A==1  iff (A0,A1)==(1,0)
    #   B==2  iff (B0,B1)==(0,1)
    #   C==1  iff (C0,C1)==(1,0)
    #
    # f(x)=1 iff A0=1,A1=0, B0=0,B1=1, C0=1,C1=0.
    #
    # Build a single multi-controlled phase using the 6 problem qubits as
    # controls, flipping (X) those that must be 0 in the control pattern so
    # that the all-ones control condition matches the desired assignment.
    #
    # Desired control values (1 means should be |1>): A0=1,A1=0,B0=0,B1=1,C0=1,C1=0
    # Flip qubits that must be 0: A1, B0, C1.

    anc = ancilla_qubits[0]

    # compute
    qc.x(A1)
    qc.x(B0)
    qc.x(C1)

    # multi-controlled X into ancilla: ancilla = AND of all 6 (after flips)
    qc.mcx([A0, A1, B0, B1, C0, C1], anc)

    # phase
    qc.z(anc)

    # uncompute mcx
    qc.mcx([A0, A1, B0, B1, C0, C1], anc)

    # uncompute flips
    qc.x(C1)
    qc.x(B0)
    qc.x(A1)
