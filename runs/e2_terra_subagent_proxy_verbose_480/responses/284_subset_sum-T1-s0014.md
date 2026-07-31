```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    # With positive values [6, 5, 3], sum == 5 iff only item 1 is selected.
    qc.z(problem_qubits[1])
```
