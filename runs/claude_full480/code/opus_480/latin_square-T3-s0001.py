from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Free cells order: (0,0)->cell0, (0,1)->cell1, (1,1)->cell2, (2,1)->cell3
    # Grid givens:
    #   row0: [ f0, f1, 1 ]
    #   row1: [ 1,  f2, 2 ]
    #   row2: [ 2,  f3, 0 ]
    # Column 1 (all free): f1, f2, f3 must be a permutation of {0,1,2}.
    # Column 0: f0, 1, 2 -> f0 must be 0.
    # Row0: f0, f1, 1 -> f0,f1 in {0,2} distinct.
    # Row1: 1, f2, 2 -> f2 must be 0.
    # Row2: 2, f3, 0 -> f3 must be 1.
    #
    # Solve constraints classically (symbolically, not enumerating gate table):
    #   f0 = 0 (col0), f2 = 0 (row1), f3 = 1 (row2).
    #   col1 needs {f1,f2,f3} = {0,1,2}; f2=0, f3=1 => f1 = 2.
    #   row0: f0=0, f1=2, given 1 -> {0,2,1} valid.
    #   col0: 0,1,2 valid. So the UNIQUE solution: f0=0,f1=2,f2=0,f3=1.
    #
    # Codes (b0=low, b1=high), value = decode(code), 11->0 too.
    #   f0 value 0: codes 00 or 11
    #   f1 value 2: code 10
    #   f2 value 0: codes 00 or 11
    #   f3 value 1: code 01
    #
    # Predicate f(x)=1 iff:
    #   (c0 in {00,11}) AND (c1==10) AND (c2 in {00,11}) AND (c3==01)
    #
    # Per-cell qubit indices:
    #   cell j: b0 = problem_qubits[2j], b1 = problem_qubits[2j+1]

    b = problem_qubits
    c0_b0, c0_b1 = b[0], b[1]
    c1_b0, c1_b1 = b[2], b[3]
    c2_b0, c2_b1 = b[4], b[5]
    c3_b0, c3_b1 = b[6], b[7]

    # Ancillas to hold per-cell predicate bits.
    a0, a1, a2, a3 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]

    # ---- compute ----
    # cell0 value 0: codes 00 or 11  <=>  b0 == b1.
    # a0 = 1 iff b0 == b1 : a0 = NOT(b0 XOR b1).
    qc.cx(c0_b0, a0)
    qc.cx(c0_b1, a0)
    qc.x(a0)            # a0 = 1 iff b0==b1

    # cell1 value 2: code 10  <=>  b0==0 and b1==1.
    # a1 = (NOT b0) AND b1.
    qc.x(c1_b0)
    qc.ccx(c1_b0, c1_b1, a1)
    qc.x(c1_b0)        # restore c1_b0

    # cell2 value 0: codes 00 or 11 <=> b0 == b1.
    qc.cx(c2_b0, a2)
    qc.cx(c2_b1, a2)
    qc.x(a2)

    # cell3 value 1: code 01 <=> b0==1 and b1==0.
    # a3 = b0 AND (NOT b1).
    qc.x(c3_b1)
    qc.ccx(c3_b0, c3_b1, a3)
    qc.x(c3_b1)        # restore c3_b1

    # ---- phase: -1 iff a0 AND a1 AND a2 AND a3 ----
    qc.h(ancilla_qubits[4])
    qc.x(ancilla_qubits[4])
    qc.mcx([a0, a1, a2, a3], ancilla_qubits[4])
    qc.x(ancilla_qubits[4])
    qc.h(ancilla_qubits[4])

    # ---- uncompute (mirror) ----
    qc.x(c3_b1)
    qc.ccx(c3_b0, c3_b1, a3)
    qc.x(c3_b1)

    qc.x(a2)
    qc.cx(c2_b1, a2)
    qc.cx(c2_b0, a2)

    qc.x(c1_b0)
    qc.ccx(c1_b0, c1_b1, a1)
    qc.x(c1_b0)

    qc.x(a0)
    qc.cx(c0_b1, a0)
    qc.cx(c0_b0, a0)
