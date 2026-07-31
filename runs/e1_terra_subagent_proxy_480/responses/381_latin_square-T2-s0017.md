```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    zero_controls = [1, 2, 3, 5]
    for qubit in zero_controls:
        qc.x(problem_qubits[qubit])

    qc.mcx(problem_qubits, ancilla_qubits[0])

    for qubit in zero_controls:
        qc.x(problem_qubits[qubit])
```
