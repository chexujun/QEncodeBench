import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Free cells order: 0:(0,2)  1:(1,2)  2:(2,1)  3:(2,2)
    # Each free cell j: b0=problem_qubits[2j], b1=problem_qubits[2j+1], code=b0+2*b1
    # Decode: 00->0, 01->1, 10->2, 11->0.
    #
    # Given grid:
    #   0 1 .
    #   1 2 .
    #   2 . .
    # Rows:
    #   row0: givens {0,1}, free cell 0  -> must be 2  (code 10)
    #   row1: givens {1,2}, free cell 1  -> must be 0  (code 00 or 11)
    #   row2: givens {2},   free cells 2,3 -> must be {0,1} in some order
    # Cols:
    #   col0: givens {0,1,2} full.
    #   col1: givens {1,2}, free cell 2 -> must be 0
    #   col2: free cells 0,1,3 -> must be {0,1,2}
    #
    # Combine constraints:
    #   fc0 = 2  (code 10) -> b0=0,b1=1
    #   fc1 = 0  (row) and col2 needs {0,1,2} among fc0,fc1,fc3; fc0=2 so fc1,fc3 = {0,1}
    #        fc1 = 0 from row1 -> fc3 = 1
    #   fc2 = 0  (col1) ; row2 needs {0,1}: fc2=0 -> fc3=1  consistent
    #   fc3 = 1  (code 01) -> b0=1,b1=0
    #
    # So the UNIQUE solution in VALUE space:
    #   fc0 value 2, fc1 value 0, fc2 value 0, fc3 value 1.
    #
    # In CODE space (surjective 11->0):
    #   fc0 value 2 : only code 10
    #   fc1 value 0 : code 00 or 11
    #   fc2 value 0 : code 00 or 11
    #   fc3 value 1 : only code 01
    #
    # Predicate f = 1 iff:
    #   fc0: b0==0 and b1==1
    #   fc1: value0  <=>  (b0==b1)   [00 or 11]
    #   fc2: value0  <=>  (b0==b1)
    #   fc3: b0==1 and b1==0

    b = problem_qubits
    fc0_b0, fc0_b1 = b[0], b[1]
    fc1_b0, fc1_b1 = b[2], b[3]
    fc2_b0, fc2_b1 = b[4], b[5]
    fc3_b0, fc3_b1 = b[6], b[7]

    # ancillas: one predicate bit per free cell condition, plus mcx workspace
    a0, a1, a2, a3 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]

    # ---- compute per-cell predicate ancillas ----

    # fc0: b0==0 and b1==1  -> a0 = (NOT b0) AND b1
    qc.x(fc0_b0)
    qc.ccx(fc0_b0, fc0_b1, a0)
    qc.x(fc0_b0)

    # fc1: b0 == b1  -> a1 = XNOR(b0,b1)
    qc.cx(fc1_b0, a1)
    qc.cx(fc1_b1, a1)
    qc.x(a1)

    # fc2: b0 == b1  -> a2 = XNOR(b0,b1)
    qc.cx(fc2_b0, a2)
    qc.cx(fc2_b1, a2)
    qc.x(a2)

    # fc3: b0==1 and b1==0  -> a3 = b0 AND (NOT b1)
    qc.x(fc3_b1)
    qc.ccx(fc3_b0, fc3_b1, a3)
    qc.x(fc3_b1)

    # ---- phase: -1 iff a0 & a1 & a2 & a3 all 1 ----
    qc.h(a3)
    qc.mcx([a0, a1, a2], a3)
    qc.h(a3)

    # ---- uncompute (mirror) ----
    qc.x(fc3_b1)
    qc.ccx(fc3_b0, fc3_b1, a3)
    qc.x(fc3_b1)

    qc.x(a2)
    qc.cx(fc2_b1, a2)
    qc.cx(fc2_b0, a2)

    qc.x(a1)
    qc.cx(fc1_b1, a1)
    qc.cx(fc1_b0, a1)

    qc.x(fc0_b0)
    qc.ccx(fc0_b0, fc0_b1, a0)
    qc.x(fc0_b0)
