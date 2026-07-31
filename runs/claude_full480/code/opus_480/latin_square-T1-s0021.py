from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Free cells: (1,1)=cell0, (1,2)=cell1
    # Grid given:
    #   row0: 1 2 0
    #   row1: 2 . .   -> (1,1)=cell0, (1,2)=cell1
    #   row2: 0 1 2
    # Row1 already has a 2 in col0. Cells must be {0,1} in some order -> row1 = 2,0,1 or 2,1,0
    # Column constraints:
    #   col1: row0=2, row2=1, so cell0 (row1,col1) must be 0.
    #   col2: row0=0, row2=2, so cell1 (row1,col2) must be 1.
    # Unique solution: cell0 = 0, cell1 = 1.
    # cell0 code must decode to 0: codes 00 or 11 -> (b0,b1) in {(0,0),(1,1)}, i.e. b0==b1.
    # cell1 code must decode to 1: code 01 only -> b0=1,b1=0.
    c0b0 = problem_qubits[0]
    c0b1 = problem_qubits[1]
    c1b0 = problem_qubits[2]
    c1b1 = problem_qubits[3]

    a0 = ancilla_qubits[0]  # cell0 valid: b0 == b1
    a1 = ancilla_qubits[1]  # cell1 valid: b0==1 and b1==0
    a2 = ancilla_qubits[2]  # combined predicate

    # compute a0 = NOT(c0b0 XOR c0b1) = (b0==b1)
    qc.cx(c0b0, a0)
    qc.cx(c0b1, a0)
    qc.x(a0)  # a0 = 1 iff b0==b1

    # compute a1 = c1b0 AND (NOT c1b1)
    qc.x(c1b1)
    qc.ccx(c1b0, c1b1, a1)
    qc.x(c1b1)

    # combined predicate a2 = a0 AND a1
    qc.ccx(a0, a1, a2)

    # phase
    qc.z(a2)

    # uncompute
    qc.ccx(a0, a1, a2)

    qc.x(c1b1)
    qc.ccx(c1b0, c1b1, a1)
    qc.x(c1b1)

    qc.x(a0)
    qc.cx(c0b1, a0)
    qc.cx(c0b0, a0)
