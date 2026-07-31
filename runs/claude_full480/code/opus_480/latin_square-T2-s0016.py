from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Free cells (row,col): j0=(1,1), j1=(1,2), j2=(2,2)
    # Grid givens:
    #   row0: 2 1 0
    #   row1: 1 . .      -> (1,0)=1
    #   row2: 0 2 .      -> (2,0)=0, (2,1)=2
    # Free cell qubits: cell j uses b0=problem_qubits[2j], b1=problem_qubits[2j+1]
    # code c = b0 + 2*b1 ; decode 00->0,01->1,10->2,11->0
    # value indicator over {0,1,2}:
    #   is0 = (NOT b0 AND NOT b1) OR (b0 AND b1)  = (b0 == b1)
    #   is1 = b0 AND NOT b1
    #   is2 = NOT b0 AND b1
    #
    # Constraints for a valid Latin square:
    #  Cell (1,1) [j0]: row1 has given 1 -> val != 1 ; col1 has given 1(r0),2(r2) -> val != 1, !=2 -> val must be 0
    #  Cell (1,2) [j1]: row1 has 1 and cell(1,1); col2 has 0(r0) -> val !=0
    #  Cell (2,2) [j2]: row2 has 0,2; col2 has 0(r0)
    #
    # Deduce: (1,1)=0. Then row1 remaining {0,2} minus 0 -> (1,2)=2. col2: r0=0, so ok.
    #         (2,2): row2 has {0,2}, needs 1 -> (2,2)=1. col2 has {0(r0),2(r1)} -> needs 1, ok.
    # Unique solution: cell0=0, cell1=2, cell2=1.
    #
    # Predicate f = is0(cell0) AND is2(cell1) AND is1(cell2)

    b0_0, b1_0 = problem_qubits[0], problem_qubits[1]
    b0_1, b1_1 = problem_qubits[2], problem_qubits[3]
    b0_2, b1_2 = problem_qubits[4], problem_qubits[5]

    # ancillas
    p0 = ancilla_qubits[0]  # cell0 is0  = (b0_0 == b1_0)
    p1 = ancilla_qubits[1]  # cell1 is2  = (NOT b0_1) AND b1_1
    p2 = ancilla_qubits[2]  # cell2 is1  = b0_2 AND (NOT b1_2)
    tgt = ancilla_qubits[3]

    # --- compute p0 = (b0_0 == b1_0) = NOT(b0_0 XOR b1_0) ---
    qc.cx(b0_0, p0)
    qc.cx(b1_0, p0)
    qc.x(p0)

    # --- compute p1 = (NOT b0_1) AND b1_1 ---
    qc.x(b0_1)
    qc.ccx(b0_1, b1_1, p1)
    qc.x(b0_1)

    # --- compute p2 = b0_2 AND (NOT b1_2) ---
    qc.x(b1_2)
    qc.ccx(b0_2, b1_2, p2)
    qc.x(b1_2)

    # --- phase: -1 iff p0 AND p1 AND p2 ---
    qc.h(tgt)
    qc.mcx([p0, p1, p2], tgt)
    qc.h(tgt)

    # --- uncompute p2 ---
    qc.x(b1_2)
    qc.ccx(b0_2, b1_2, p2)
    qc.x(b1_2)

    # --- uncompute p1 ---
    qc.x(b0_1)
    qc.ccx(b0_1, b1_1, p1)
    qc.x(b0_1)

    # --- uncompute p0 ---
    qc.x(p0)
    qc.cx(b1_0, p0)
    qc.cx(b0_0, p0)
