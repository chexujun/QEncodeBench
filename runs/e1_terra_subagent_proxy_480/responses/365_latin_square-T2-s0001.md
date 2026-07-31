```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    p0, p2, p4, p5 = (
        problem_qubits[0],
        problem_qubits[2],
        problem_qubits[4],
        problem_qubits[5],
    )
    target = ancilla_qubits[0]

    qc.x(p0)
    qc.x(p2)
    qc.x(p5)

    qc.mcx([p0, p2, p4, p5], target)
    qc.z(target)
    qc.mcx([p0, p2, p4, p5], target)

    qc.x(p5)
    qc.x(p2)
    qc.x(p0)
```
