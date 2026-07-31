from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Free cells: (1,1) = free cell 0, (2,2) = free cell 1
    # Grid givens:
    #   row0: 2 0 1
    #   row1: 1 . 0   -> free cell 0 at (1,1)
    #   row2: 0 1 .   -> free cell 1 at (2,2)
    # Columns:
    #   col0: 2 1 0
    #   col1: 0 . 1   -> free cell 0 at (1,1)
    #   col2: 1 0 .   -> free cell 1 at (2,2)
    #
    # Row1 already has {1,0}, so free cell 0 must be value 2.
    # Col1 already has {0,1}, so free cell 0 must be value 2.  Consistent: cell0 == 2.
    # Row2 already has {0,1}, so free cell 1 must be value 2.
    # Col2 already has {1,0}, so free cell 1 must be value 2.  Consistent: cell1 == 2.
    #
    # Decoding: code c = b0 + 2*b1 ; 00->0, 01->1, 10->2, 11->0.
    # Value 2 <=> code == 10 <=> b0==0 and b1==1.
    #
    # So f(x)=1 iff (cell0: b0=0,b1=1) and (cell1: b0=0,b1=1).
    # problem_qubits[0]=cell0 b0, [1]=cell0 b1, [2]=cell1 b0, [3]=cell1 b1.

    q0b0 = problem_qubits[0]
    q0b1 = problem_qubits[1]
    q1b0 = problem_qubits[2]
    q1b1 = problem_qubits[3]

    # We want phase -1 iff q0b0=0, q0b1=1, q1b0=0, q1b1=1.
    # Flip the "0"-required bits so all four controls are active-high on |1>.
    qc.x(q0b0)
    qc.x(q1b0)

    # 4-controlled Z: phase -1 iff all four qubits are 1.
    # Use mcp(pi, controls, target) which applies -1 when all controls and target are 1.
    qc.mcp(np.pi, [q0b0, q0b1, q1b0], q1b1)

    # Uncompute the X flips.
    qc.x(q0b0)
    qc.x(q1b0)
