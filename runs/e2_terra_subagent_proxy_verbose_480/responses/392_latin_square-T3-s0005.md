```python
from math import pi

def build_oracle(qc, problem_qubits, ancilla_qubits):
    eq_cell_1 = ancilla_qubits[0]
    eq_cell_2 = ancilla_qubits[1]

    # Value 0 is encoded by 00 or 11, i.e. the two code bits are equal.
    qc.x(eq_cell_1)
    qc.cx(problem_qubits[2], eq_cell_1)
    qc.cx(problem_qubits[3], eq_cell_1)

    qc.x(eq_cell_2)
    qc.cx(problem_qubits[4], eq_cell_2)
    qc.cx(problem_qubits[5], eq_cell_2)

    # The unique valid decoded completion is [1, 0, 0, 2].
    # Convert its negative controls to positive controls.
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[6])

    qc.mcp(
        pi,
        [
            problem_qubits[0],
            problem_qubits[1],
            eq_cell_1,
            eq_cell_2,
            problem_qubits[6],
        ],
        problem_qubits[7],
    )

    qc.x(problem_qubits[6])
    qc.x(problem_qubits[1])

    # Uncompute the equality predicates.
    qc.cx(problem_qubits[5], eq_cell_2)
    qc.cx(problem_qubits[4], eq_cell_2)
    qc.x(eq_cell_2)

    qc.cx(problem_qubits[3], eq_cell_1)
    qc.cx(problem_qubits[2], eq_cell_1)
    qc.x(eq_cell_1)
```
