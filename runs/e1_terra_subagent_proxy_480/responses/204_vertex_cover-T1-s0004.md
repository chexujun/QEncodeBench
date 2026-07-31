```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    q0,q1,q2,q3=problem_qubits
    for zeros in ((q0,q3),(q0,q1)):
        qc.x(list(zeros)); qc.h(q3); qc.mcx([q0,q1,q2],q3); qc.h(q3); qc.x(list(zeros))
```
