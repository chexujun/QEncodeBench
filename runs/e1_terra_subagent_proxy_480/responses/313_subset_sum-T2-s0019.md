```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    qc.mcx(problem_qubits, ancilla_qubits[0], ctrl_state="0000")
```
