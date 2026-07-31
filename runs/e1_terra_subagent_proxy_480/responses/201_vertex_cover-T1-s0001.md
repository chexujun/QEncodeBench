```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    q = problem_qubits
    for zeros in ([1, 3], [1, 2], [0, 3]):
        for i in zeros:
            qc.x(q[i])
        qc.h(q[3])
        qc.mcx([q[0], q[1], q[2]], q[3])
        qc.h(q[3])
        for i in zeros:
            qc.x(q[i])
```
