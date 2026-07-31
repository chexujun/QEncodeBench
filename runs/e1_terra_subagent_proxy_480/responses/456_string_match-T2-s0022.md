```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    for offset in range(3):
        zero_controls = [problem_qubits[offset + 1], problem_qubits[offset + 2]]
        target = problem_qubits[offset + 3]
        for qubit in zero_controls:
            qc.x(qubit)
        qc.ccz(zero_controls[0], zero_controls[1], target)
        for qubit in reversed(zero_controls):
            qc.x(qubit)
```
