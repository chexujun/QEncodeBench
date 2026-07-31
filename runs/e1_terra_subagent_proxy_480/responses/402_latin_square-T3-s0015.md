```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    zero_bits = [0, 1, 3, 5, 6, 7]
    for i in zero_bits: qc.x(problem_qubits[i])
    target = problem_qubits[7]
    qc.h(target); qc.mcx(problem_qubits[:7], target); qc.h(target)
    for i in zero_bits: qc.x(problem_qubits[i])
```
