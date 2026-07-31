from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Free cells: (2,0)=cellA, (2,1)=cellB. Row 2 must be a permutation of {0,1,2}.
    # Given grid columns: col0 has {1,0}, col1 has {2,1}, col2 has {0,2,1}.
    # cellA (row2,col0): allowed values = {0,1,2}\{1,0} = {2}. So cellA must be 2.
    # cellB (row2,col1): allowed values = {0,1,2}\{2,1} = {0}. So cellB must be 0.
    # Row constraint: {cellA,cellB,1} all-different -> {2,0,1} OK automatically.
    # So valid iff cellA==2 and cellB==0.
    # Decoding: value2 <-> code 10 (b0=0,b1=1). value0 <-> code 00 or 11.
    # cellA qubits: b0=problem_qubits[0], b1=problem_qubits[1]. Need b0=0,b1=1.
    # cellB qubits: b0=problem_qubits[2], b1=problem_qubits[3]. Need value0: code 00 or 11 -> b0==b1.

    a0, a1, a2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    a3 = problem_qubits[3]
    anc = ancilla_qubits

    # Predicate P = (a0==0 AND a1==1) AND (a2==a3)
    # anc0 = 1 iff a0==0 and a1==1
    qc.x(a0)  # now a0'==1 iff original a0==0
    qc.ccx(a0, a1, anc[0])
    qc.x(a0)  # restore a0

    # anc1 = 1 iff a2==a3 : a2 XNOR a3
    qc.cx(a2, anc[1])
    qc.cx(a3, anc[1])
    qc.x(anc[1])  # anc1 = NOT(a2 xor a3) = (a2==a3)

    # phase on anc0 AND anc1
    qc.cz(anc[0], anc[1])

    # uncompute anc1
    qc.x(anc[1])
    qc.cx(a3, anc[1])
    qc.cx(a2, anc[1])

    # uncompute anc0
    qc.x(a0)
    qc.ccx(a0, a1, anc[0])
    qc.x(a0)
