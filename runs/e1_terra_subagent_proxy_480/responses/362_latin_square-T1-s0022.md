```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    a_lo, a_hi, b_lo, b_hi = problem_qubits[:4]
    target = ancilla_qubits[0]
    qc.x([a_lo, a_hi, b_hi])
    qc.mcx([a_lo, a_hi, b_lo, b_hi], target)
    qc.x([a_lo, a_hi])
    qc.mcx([a_lo, a_hi, b_lo, b_hi], target)
    qc.x(b_hi)
```
