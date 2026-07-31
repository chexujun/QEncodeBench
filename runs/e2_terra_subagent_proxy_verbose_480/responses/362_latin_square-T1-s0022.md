```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    a0, a1 = ancilla_qubits[:2]

    qc.cx(problem_qubits[0], a0)
    qc.cx(problem_qubits[1], a0)
    qc.cx(problem_qubits[2], a1)
    qc.cx(problem_qubits[3], a1)

    qc.x(a0)
    qc.x(a1)
    qc.cz(a0, a1)
    qc.x(a1)
    qc.x(a0)

    qc.cx(problem_qubits[3], a1)
    qc.cx(problem_qubits[2], a1)
    qc.cx(problem_qubits[1], a0)
    qc.cx(problem_qubits[0], a0)
```
