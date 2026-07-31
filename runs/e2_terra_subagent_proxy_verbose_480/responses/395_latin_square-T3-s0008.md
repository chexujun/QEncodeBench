```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    p = problem_qubits
    eq_cell1 = ancilla_qubits[0]
    eq_cell2 = ancilla_qubits[1]
    flag = ancilla_qubits[2]

    # Compute whether cells 1 and 2 decode to value 0.
    # Under the given encoding, value 0 iff the two code bits are equal.
    qc.x(eq_cell1)
    qc.cx(p[2], eq_cell1)
    qc.cx(p[3], eq_cell1)

    qc.x(eq_cell2)
    qc.cx(p[4], eq_cell2)
    qc.cx(p[5], eq_cell2)

    # The unique valid decoded completion is [1, 0, 0, 1].
    # Value 1 has code 01, so its high bit is a negative control.
    qc.x(p[1])
    qc.x(p[7])

    controls = [p[0], p[1], eq_cell1, eq_cell2, p[6], p[7]]
    qc.mcx(controls, flag)
    qc.z(flag)
    qc.mcx(controls, flag)

    qc.x(p[7])
    qc.x(p[1])

    # Uncompute the equality predicates.
    qc.cx(p[5], eq_cell2)
    qc.cx(p[4], eq_cell2)
    qc.x(eq_cell2)

    qc.cx(p[3], eq_cell1)
    qc.cx(p[2], eq_cell1)
    qc.x(eq_cell1)
```
