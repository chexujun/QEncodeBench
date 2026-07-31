```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    s1, s2, s3 = problem_qubits[1], problem_qubits[2], problem_qubits[3]
    ancilla = ancilla_qubits[0]

    qc.x(s3)
    qc.ccx(s1, s2, ancilla)
    qc.cz(ancilla, s3)
    qc.ccx(s1, s2, ancilla)
    qc.x(s3)
```
