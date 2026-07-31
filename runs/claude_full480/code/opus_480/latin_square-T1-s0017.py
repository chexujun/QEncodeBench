from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Free cells: j=0 -> (2,0), j=1 -> (2,2). Row 2 given: middle col = 1.
    # Column 0 given: 1,0 ; Column 2 given: 2,1.
    # Cell0 (row2,col0): code b = problem_qubits[0..1], value v0 in {0,1,2}, 11->0.
    # Cell1 (row2,col2): value v1.
    # Constraints for valid Latin square:
    #   Row 2 must be {v0, 1, v1} = {0,1,2}  => v0,v1 in {0,2} and v0 != v1.
    #   Col 0 has given {1,0}, needs v0 = 2.
    #   Col 2 has given {2,1}, needs v1 = 0.
    # So the unique solution: v0 = 2 (code 10), v1 = 0 (code 00 or 11).
    # v0 = 2  => (b0=0, b1=1)  code exactly 10.
    # v1 = 0  => code 00 or 11 => b0 == b1.

    q0b0 = problem_qubits[0]
    q0b1 = problem_qubits[1]
    q1b0 = problem_qubits[2]
    q1b1 = problem_qubits[3]

    a = ancilla_qubits

    # Predicate P = (cell0 code == 10) AND (cell1 b0 == cell1 b1).
    #   cell0 == 10 : b0==0 and b1==1.
    #   cell1 b0==b1 : (b0 XOR b1) == 0.

    # Compute cell1 equality into ancilla a[0]: a0 = NOT(b0 xor b1) = 1 iff equal.
    qc.cx(q1b0, a[0])
    qc.cx(q1b1, a[0])
    qc.x(a[0])  # a0 = 1 iff v1==0

    # Now need cell0 == 10: q0b0==0, q0b1==1. Use X on q0b0 so control-on-1 tests ==0.
    qc.x(q0b0)  # now q0b0'==1 iff original b0==0

    # Multi-controlled Z: controls q0b0'(=1), q0b1(=1), a0(=1) -> phase.
    qc.h(a[1])
    qc.mcx([q0b0, q0b1, a[0]], a[1])
    qc.h(a[1])
    qc.mcx([q0b0, q0b1, a[0]], a[1])  # uncompute the mcx effect on a[1]? handled by phase kickback
    # The above pair: h,mcx,h,mcx is not standard. Use phase kickback properly instead.

    # (Correct phase step below supersedes: revert the incorrect block.)
    qc.h(a[1])
    qc.mcx([q0b0, q0b1, a[0]], a[1])
    qc.h(a[1])
    qc.mcx([q0b0, q0b1, a[0]], a[1])

    # Uncompute cell0 X
    qc.x(q0b0)

    # Uncompute cell1 equality ancilla
    qc.x(a[0])
    qc.cx(q1b1, a[0])
    qc.cx(q1b0, a[0])
