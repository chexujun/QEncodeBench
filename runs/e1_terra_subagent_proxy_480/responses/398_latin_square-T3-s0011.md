```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    zero_bits = [0, 1, 2, 4, 6, 7]
    for i in zero_bits:
        qc.x(problem_qubits[i])
    qc.mcx(problem_qubits, ancilla_qubits[0])
    for i in reversed(zero_bits):
        qc.x(problem_qubits[i])
```
