from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Free cells: (0,1)=cell0, (1,2)=cell1.
    # Grid givens:
    #  row0: 1 . 2   -> cell0 in row0 (with 1,2), col1 has given 2 (row2)
    #  row1: 0 2 .   -> cell1 in row1 (with 0,2), col2 has given 2 (row0)
    #  row2: 2 1 0
    #
    # Constraints reduce to: cell0 must be value 0, cell1 must be value 1.
    # cell0 low=pq0 high=pq1 ; cell1 low=pq2 high=pq3.
    # code->value: 00->0,01->1,10->2,11->0.
    # cell0 == value 0  iff code in {00,11}  iff b0 == b1  (pq0 == pq1)
    # cell1 == value 1  iff code == 01        iff pq2==1 and pq3==0

    p0, p1, p2, p3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    a = ancilla_qubits

    # a0 = (cell0 is value0) = NOT(p0 XOR p1)
    qc.cx(p0, a[0])
    qc.cx(p1, a[0])
    qc.x(a[0])          # a0 = 1 iff p0==p1

    # a1 = (cell1 is value1) = p2 AND (NOT p3)
    qc.x(p3)
    qc.ccx(p2, p3, a[1])
    qc.x(p3)            # restore p3; a1 = 1 iff p2==1 and p3==0

    # phase -1 iff a0==1 and a1==1
    qc.cz(a[0], a[1])

    # uncompute a1
    qc.x(p3)
    qc.ccx(p2, p3, a[1])
    qc.x(p3)

    # uncompute a0
    qc.x(a[0])
    qc.cx(p1, a[0])
    qc.cx(p0, a[0])
