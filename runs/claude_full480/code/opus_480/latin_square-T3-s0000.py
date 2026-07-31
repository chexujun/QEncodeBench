from qiskit import QuantumCircuit
from math import pi


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Grid layout (rows x cols), givens and free-cell placement:
    #   row0: [given 1] [free0] [given 2]
    #   row1: [given 2] [free1] [given 0]
    #   row2: [free2 ] [given 2] [free3 ]
    # Free cell j -> code (b0,b1) on problem_qubits[2j], problem_qubits[2j+1]
    # decode: 00->0, 01->1, 10->2, 11->0
    #
    # For a valid Latin square we need, given the fixed givens:
    #   row0 has {1,2,val0}=>{0,1,2} => val0 must be 0
    #   row1 has {2,0,val1}=>{0,1,2} => val1 must be 1
    #   row2 has {val2,2,val3}       => {val2,val3}={0,1} in some order
    #   col0 has {1,2,val2}          => val2 must be 0
    #   col1 has {val0,val1,2}       => {val0,val1}={0,1} in some order
    #   col2 has {2,0,val3}          => val3 must be 1
    # Combined necessary&sufficient: val0=0, val1=1, val2=0, val3=1.
    # (These automatically satisfy the row2/col1 pair constraints.)
    #
    # decode==0 iff code in {00,11} iff (b0==b1).
    # decode==1 iff code==01 iff (b0==1 and b1==0).
    #
    # Predicate = [v0==0] AND [v1==1] AND [v2==0] AND [v3==1].

    b0 = [problem_qubits[2 * j] for j in range(4)]
    b1 = [problem_qubits[2 * j + 1] for j in range(4)]

    # Ancillas: a0..a3 hold per-cell "is-correct" flags; a4 unused-spare, a5 spare.
    a = ancilla_qubits

    # --- compute per-cell correctness flags ---
    # Cell0 correct iff v0==0 iff b0[0]==b1[0]. flag = NOT(b0 xor b1).
    qc.cx(b0[0], a[0])
    qc.cx(b1[0], a[0])
    qc.x(a[0])  # a0 = 1 iff cell0 decodes to 0

    # Cell2 correct iff v2==0 iff b0[2]==b1[2].
    qc.cx(b0[2], a[1])
    qc.cx(b1[2], a[1])
    qc.x(a[1])  # a1 = 1 iff cell2 decodes to 0

    # Cell1 correct iff v1==1 iff (b0[1]==1 and b1[1]==0).
    # flag = b0[1] AND (NOT b1[1])
    qc.x(b1[1])
    qc.ccx(b0[1], b1[1], a[2])
    qc.x(b1[1])  # a2 = 1 iff cell1 decodes to 1

    # Cell3 correct iff v3==1 iff (b0[3]==1 and b1[3]==0).
    qc.x(b1[3])
    qc.ccx(b0[3], b1[3], a[3])
    qc.x(b1[3])  # a3 = 1 iff cell3 decodes to 1

    # --- combine: phase -1 iff all four flags == 1 ---
    # Use a[4] to AND a0&a1, then mcp over a4,a2,a3.
    qc.ccx(a[0], a[1], a[4])
    # controlled-Z style multi-control phase on (a4, a2, a3)
    qc.h(a[5])
    qc.mcx([a[4], a[2], a[3]], a[5])
    qc.z(a[5])
    qc.mcx([a[4], a[2], a[3]], a[5])
    qc.h(a[5])
    qc.ccx(a[0], a[1], a[4])

    # --- uncompute flags (mirror) ---
    qc.x(b1[3])
    qc.ccx(b0[3], b1[3], a[3])
    qc.x(b1[3])

    qc.x(b1[1])
    qc.ccx(b0[1], b1[1], a[2])
    qc.x(b1[1])

    qc.x(a[1])
    qc.cx(b1[2], a[1])
    qc.cx(b0[2], a[1])

    qc.x(a[0])
    qc.cx(b1[0], a[0])
    qc.cx(b0[0], a[0])
