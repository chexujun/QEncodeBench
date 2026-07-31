```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    q = problem_qubits
    target = ancilla_qubits[0]
    for a, b in ((q[0], q[1]), (q[4], q[5]), (q[6], q[7])): qc.cx(a, b)
    for bit in (q[1], q[3], q[5], q[7]): qc.x(bit)
    qc.mcx([q[1], q[2], q[3], q[5], q[7]], target)
    for bit in (q[1], q[3], q[5], q[7]): qc.x(bit)
    for a, b in reversed(((q[0], q[1]), (q[4], q[5]), (q[6], q[7]))): qc.cx(a, b)
```
