import numpy as np
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Free cells in order: (0,1), (1,0), (2,2)
    # Grid givens:
    #   row0: 0 . 1   -> free cell 0 at (0,1); row0 has {0,1}; col1 has given {1(r1)? } wait compute below
    #   row1: . 1 0   -> free cell 1 at (1,0); row1 has {1,0}
    #   row2: 1 0 .   -> free cell 2 at (2,2); row2 has {1,0}
    #
    # For a valid Latin square the only missing value in each row/col must be placed.
    # row0 missing value = 2 (has 0,1) -> cell0 must be 2
    # row1 missing value = 2 (has 1,0) -> cell1 must be 2
    # row2 missing value = 2 (has 1,0) -> cell2 must be 2
    # Column checks:
    #   col1: given row1=1, row2=0; cell0 at (0,1) must be 2 -> col1={2,1,0} ok
    #   col0: given row0=0, row2=1; cell1 at (1,0) must be 2 -> col0={0,2,1} ok
    #   col2: given row0=1, row1=0; cell2 at (2,2) must be 2 -> col2={1,0,2} ok
    # So f(x)=1 iff every free cell decodes to value 2.
    # value 2 <=> code 10 <=> b0=0, b1=1  (code 11 decodes to 0, not 2).
    # Condition per cell j: b0(2j)=0 AND b1(2j+1)=1.

    q = problem_qubits
    b0 = [q[0], q[2], q[4]]  # low bits, must be 0
    b1 = [q[1], q[3], q[5]]  # high bits, must be 1

    controls = b0 + b1

    # For b0 bits we need value 0 -> flip so control-on-1 works
    for c in b0:
        qc.x(c)
    # b1 bits need value 1 -> already correct as controls-on-1

    # Multi-controlled Z: phase -1 iff all controls are 1
    target = controls[-1]
    rest = controls[:-1]
    qc.h(target)
    qc.mcx(rest, target, ancilla_qubits[0], mode='v-chain')
    qc.h(target)

    # Uncompute the X flips
    for c in b0:
        qc.x(c)
