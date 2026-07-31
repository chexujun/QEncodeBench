```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, q2, q3 = problem_qubits

    for zero_controls in ((q1, q3), (q0, q3)):
        for qubit in zero_controls:
            qc.x(qubit)
        qc.h(q3)
        qc.mcx([q0, q1, q2], q3)
        qc.h(q3)
        for qubit in zero_controls:
            qc.x(qubit)
```
