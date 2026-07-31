```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    a0, a1, a2, a3, flag = ancilla_qubits[:5]

    # Value 0 is encoded by equal low/high bits: 00 or 11.
    for low, high, ancilla in (
        (problem_qubits[0], problem_qubits[1], a0),  # cell (0, 2)
        (problem_qubits[4], problem_qubits[5], a2),  # cell (1, 1)
        (problem_qubits[6], problem_qubits[7], a3),  # cell (2, 0)
    ):
        qc.cx(low, ancilla)
        qc.cx(high, ancilla)
        qc.x(ancilla)

    # Cell (1, 0) must have value 1: low=1, high=0.
    qc.x(problem_qubits[3])

    qc.mcx([a0, problem_qubits[2], problem_qubits[3], a2, a3], flag)
    qc.z(flag)
    qc.mcx([a0, problem_qubits[2], problem_qubits[3], a2, a3], flag)

    qc.x(problem_qubits[3])

    # Uncompute the value-0 tests.
    for low, high, ancilla in (
        (problem_qubits[6], problem_qubits[7], a3),
        (problem_qubits[4], problem_qubits[5], a2),
        (problem_qubits[0], problem_qubits[1], a0),
    ):
        qc.x(ancilla)
        qc.cx(high, ancilla)
        qc.cx(low, ancilla)
```
