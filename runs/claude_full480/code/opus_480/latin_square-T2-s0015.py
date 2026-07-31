import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Free cells in order: (0,0), (1,2), (2,1)
    # cell j bits: b0 = problem_qubits[2j], b1 = problem_qubits[2j+1], code = b0 + 2*b1
    # decode: 00->0, 01->1, 10->2, 11->0
    #
    # Grid (with free cells F0,F1,F2):
    #   F0  2   0
    #    0  1  F1
    #    2  F2  1
    #
    # Row constraints:
    #   Row0: {F0, 2, 0} all distinct  => F0 == 1
    #   Row1: {0, 1, F1} all distinct  => F1 == 2
    #   Row2: {2, F2, 1} all distinct  => F2 == 0
    # Column constraints:
    #   Col0: {F0, 0, 2} distinct      => F0 == 1
    #   Col1: {2, 1, F2} distinct      => F2 == 0
    #   Col2: {0, F1, 1} distinct      => F1 == 2
    #
    # So predicate: F0==1 AND F1==2 AND F2==0.
    # value==1 <=> code==01 <=> b0=1,b1=0
    # value==2 <=> code==10 <=> b0=0,b1=1
    # value==0 <=> code in {00,11} <=> b0==b1
    #
    # Encode each cell's "correct value" indicator into an ancilla, AND them,
    # phase, then uncompute.

    b0_0, b1_0 = problem_qubits[0], problem_qubits[1]  # F0
    b0_1, b1_1 = problem_qubits[2], problem_qubits[3]  # F1
    b0_2, b1_2 = problem_qubits[4], problem_qubits[5]  # F2

    a0 = ancilla_qubits[0]  # F0 == 1  indicator
    a1 = ancilla_qubits[1]  # F1 == 2  indicator
    a2 = ancilla_qubits[2]  # F2 == 0  indicator
    ax = ancilla_qubits[3]  # helper for a2 (b0==b1)
    af = ancilla_qubits[4]  # final AND

    # --- compute a0 : F0 == 1  (b0=1, b1=0) ---
    qc.x(b1_0)
    qc.ccx(b0_0, b1_0, a0)
    qc.x(b1_0)

    # --- compute a1 : F1 == 2  (b0=0, b1=1) ---
    qc.x(b0_1)
    qc.ccx(b0_1, b1_1, a1)
    qc.x(b0_1)

    # --- compute a2 : F2 == 0  (b0 == b1) ---
    # ax = b0 XOR b1 ; then a2 = NOT ax
    qc.cx(b0_2, ax)
    qc.cx(b1_2, ax)
    qc.x(ax)
    qc.cx(ax, a2)
    qc.x(ax)
    # uncompute ax
    qc.cx(b1_2, ax)
    qc.cx(b0_2, ax)

    # --- final AND: af = a0 AND a1 AND a2 ---
    qc.mcx([a0, a1, a2], af)

    # --- phase ---
    qc.z(af)

    # --- uncompute af ---
    qc.mcx([a0, a1, a2], af)

    # --- uncompute a2 ---
    qc.cx(b0_2, ax)
    qc.cx(b1_2, ax)
    qc.x(ax)
    qc.cx(ax, a2)
    qc.x(ax)
    qc.cx(b1_2, ax)
    qc.cx(b0_2, ax)

    # --- uncompute a1 ---
    qc.x(b0_1)
    qc.ccx(b0_1, b1_1, a1)
    qc.x(b0_1)

    # --- uncompute a0 ---
    qc.x(b1_0)
    qc.ccx(b0_0, b1_0, a0)
    qc.x(b1_0)
