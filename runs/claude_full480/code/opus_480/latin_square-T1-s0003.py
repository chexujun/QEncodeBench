import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Grid (given):
    #   row0: 0 2 1
    #   row1: 1 . 2   free cell A at (1,1)
    #   row2: 2 1 .   free cell B at (2,2)
    #
    # Free cell A = problem_qubits[0:2] (b0=pq[0], b1=pq[1]), code c = b0 + 2 b1.
    # Free cell B = problem_qubits[2:4] (b0=pq[2], b1=pq[3]).
    #
    # Decode surjective: 00->0, 01->1, 10->2, 11->0.
    # Row1 already has {1,2}; the missing value is 0. So A must decode to 0.
    #   A decodes to 0  <=>  code in {00, 11}  <=>  b0 == b1 (a0 == a1).
    # Col1 (index 1) already has {2,1} (row0 col1=2, row2 col1=1); missing 0. Consistent: A=0.
    # Row2 already has {2,1}; missing 0. So B must decode to 0.
    #   B decodes to 0  <=>  b0 == b1 (b2 == b3).
    # Col2 (index 2) already has {1,2}; missing 0. Consistent: B=0.
    #
    # So f(x)=1  iff  (pq0 == pq1)  AND  (pq2 == pq3).

    pq0, pq1, pq2, pq3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    eqA = ancilla_qubits[0]
    eqB = ancilla_qubits[1]

    # eqA = 1 iff pq0 == pq1  (XNOR)
    qc.cx(pq0, eqA)
    qc.cx(pq1, eqA)
    qc.x(eqA)

    # eqB = 1 iff pq2 == pq3  (XNOR)
    qc.cx(pq2, eqB)
    qc.cx(pq3, eqB)
    qc.x(eqB)

    # phase -1 iff eqA AND eqB
    qc.cz(eqA, eqB)

    # uncompute
    qc.x(eqB)
    qc.cx(pq3, eqB)
    qc.cx(pq2, eqB)

    qc.x(eqA)
    qc.cx(pq1, eqA)
    qc.cx(pq0, eqA)
