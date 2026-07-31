from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    P = problem_qubits
    A = ancilla_qubits

    # Free cells order: (0,0)=j0, (1,0)=j1, (2,1)=j2, (2,2)=j3
    # Given grid:
    #   row0: . 1 2   -> cell0 at (0,0)
    #   row1: . 0 1   -> cell1 at (1,0)
    #   row2: 1 . .   -> cell2 at (2,1), cell3 at (2,2)
    #
    # Value of free cell j from its 2 qubits (b0=P[2j], b1=P[2j+1]):
    #   00->0, 01->1, 10->2, 11->0   (surjective).
    #
    # Constraints (each must hold; value in {0,1,2}):
    #   Row0: {c0, 1, 2} all diff  -> c0 == 0
    #   Row1: {c1, 0, 1} all diff  -> c1 == 2
    #   Row2: {1, c2, c3} all diff -> c2,c3 in {0,2}, c2!=c3
    #   Col0: {c0, c1, 1} all diff -> c0!=c1, c0!=1, c1!=1
    #   Col1: {1, 0, c2} all diff  -> c2 == 2
    #   Col2: {2, 1, c3} all diff  -> c3 == 0
    #
    # Combining: c0==0, c1==2, c2==2, c3==0. These automatically satisfy
    # row2 (0? wait c2==2,c3==0 -> {1,2,0} valid) and col0 ({0,2,1} valid).
    # So f=1 iff c0==0 AND c1==2 AND c2==2 AND c3==0.
    #
    # Encode predicate for each cell into one ancilla each, then MCX phase.

    def val_is(cell, value, anc):
        # Set anc (starts |0>) to 1 iff decoded value of `cell` == value.
        b0 = P[2 * cell]
        b1 = P[2 * cell + 1]
        if value == 0:
            # value 0 <=> code 00 or 11 <=> b0 == b1
            # anc = NOT(b0 XOR b1)
            qc.cx(b0, anc)
            qc.cx(b1, anc)
            qc.x(anc)
        elif value == 1:
            # code 01 : b0=1,b1=0
            qc.x(b1)
            qc.ccx(b0, b1, anc)
            qc.x(b1)
        elif value == 2:
            # code 10 : b0=0,b1=1
            qc.x(b0)
            qc.ccx(b0, b1, anc)
            qc.x(b0)

    def val_is_inv(cell, value, anc):
        b0 = P[2 * cell]
        b1 = P[2 * cell + 1]
        if value == 0:
            qc.x(anc)
            qc.cx(b1, anc)
            qc.cx(b0, anc)
        elif value == 1:
            qc.x(b1)
            qc.ccx(b0, b1, anc)
            qc.x(b1)
        elif value == 2:
            qc.x(b0)
            qc.ccx(b0, b1, anc)
            qc.x(b0)

    targets = [(0, 0), (1, 2), (2, 2), (3, 0)]

    # Compute each predicate into ancilla A[0..3]
    for k, (cell, value) in enumerate(targets):
        val_is(cell, value, A[k])

    # Phase -1 iff all four ancillas are 1
    qc.h(A[3])
    qc.mcx([A[0], A[1], A[2]], A[3])
    qc.h(A[3])

    # Uncompute
    for k in reversed(range(len(targets))):
        cell, value = targets[k]
        val_is_inv(cell, value, A[k])
