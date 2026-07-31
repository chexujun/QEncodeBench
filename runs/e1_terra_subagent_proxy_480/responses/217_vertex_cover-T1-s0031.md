```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    a, b, c, d = problem_qubits

    qc.x(b)
    qc.x(d)
    qc.h(d)
    qc.mcx([a, b, c], d)
    qc.h(d)
    qc.x(b)
    qc.x(d)

    qc.x(a)
    qc.x(c)
    qc.h(d)
    qc.mcx([a, b, c], d)
    qc.h(d)
    qc.x(a)
    qc.x(c)
```
