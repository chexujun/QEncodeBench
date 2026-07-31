import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Free cells (row, col): j=0 -> (0,1), j=1 -> (0,2), j=2 -> (1,0)
    # Each free cell j: b0 = problem_qubits[2j], b1 = problem_qubits[2j+1]
    # Decode: 00->0, 01->1, 10->2, 11->0  (surjective)
    #
    # Grid (rows):
    #   row0: 2   V0  V1     -> V0=(0,1)=cell0, V1=(0,2)=cell1
    #   row1: V2  2   0      -> V2=(1,0)=cell2
    #   row2: 0   1   2
    #
    # Latin square constraints reduce to unique assignment.
    # Row0 already has 2. Cells V0,V1 must be {0,1} in some order, and neither = 2.
    # Row1 already has 2 and 0. Cell V2 must be 1 (not 2, not 0).
    # Column constraints:
    #   col0: V2(row0? no) -- col0 entries: row0=2, row1=V2, row2=0 -> V2 != 2, V2 != 0 -> V2=1
    #   col1: row0=V0, row1=2, row2=1 -> V0 != 2, V0 != 1 -> V0=0
    #   col2: row0=V1, row1=0, row2=2 -> V1 != 0, V1 != 2 -> V1=1
    # Row0: {V0,V1} with V0=0,V1=1 -> {0,1,2} valid. Consistent.
    #
    # So the UNIQUE solution values: V0=0, V1=1, V2=1.
    # In codes (surjective): value 0 codes = {00,11}, value 1 code = {01},
    #   value 2 code = {10}.
    #
    # f(x)=1 iff  V0 in {0}, V1 in {1}, V2 in {1}
    #   V0 == 0 : code in {00, 11}  -> (b0==b1)  i.e. b0 XOR b1 == 0
    #   V1 == 1 : code == 01        -> b0==1 and b1==0
    #   V2 == 1 : code == 01        -> b0==1 and b1==0

    c0b0, c0b1 = problem_qubits[0], problem_qubits[1]
    c1b0, c1b1 = problem_qubits[2], problem_qubits[3]
    c2b0, c2b1 = problem_qubits[4], problem_qubits[5]

    # Predicate ancillas
    p0 = ancilla_qubits[0]  # V0 == 0  <=> b0 XOR b1 == 0
    p1 = ancilla_qubits[1]  # V1 == 1  <=> b0=1,b1=0
    p2 = ancilla_qubits[2]  # V2 == 1  <=> b0=1,b1=0
    tgt = ancilla_qubits[3]  # AND of all three

    # Compute p0 = NOT(b0 XOR b1)
    qc.cx(c0b0, p0)
    qc.cx(c0b1, p0)
    qc.x(p0)  # p0 = 1 iff b0==b1

    # Compute p1 = b0 AND (NOT b1) for cell1
    qc.x(c1b1)
    qc.ccx(c1b0, c1b1, p1)
    qc.x(c1b1)

    # Compute p2 = b0 AND (NOT b1) for cell2
    qc.x(c2b1)
    qc.ccx(c2b0, c2b1, p2)
    qc.x(c2b1)

    # tgt = p0 AND p1 AND p2
    qc.mcx([p0, p1, p2], tgt)

    # Phase
    qc.z(tgt)

    # Uncompute (mirror)
    qc.mcx([p0, p1, p2], tgt)

    qc.x(c2b1)
    qc.ccx(c2b0, c2b1, p2)
    qc.x(c2b1)

    qc.x(c1b1)
    qc.ccx(c1b0, c1b1, p1)
    qc.x(c1b1)

    qc.x(p0)
    qc.cx(c0b1, p0)
    qc.cx(c0b0, p0)
