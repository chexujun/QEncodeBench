```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    a0, a1, b0, b1, c0, c1, d0, d1 = problem_qubits
    target = ancilla_qubits[0]
    qc.cx(a0, a1)
    qc.cx(c0, c1)
    qc.cx(d0, d1)
    qc.x(a1); qc.x(b0); qc.x(b1); qc.x(c1); qc.x(d1)
    qc.x(target); qc.h(target)
    qc.mcx([a1, b0, b1, c1, d1], target)
    qc.h(target); qc.x(target)
    qc.x(a1); qc.x(b0); qc.x(b1); qc.x(c1); qc.x(d1)
    qc.cx(d0, d1); qc.cx(c0, c1); qc.cx(a0, a1)
```
