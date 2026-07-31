```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    controls = problem_qubits[:3]
    ancilla = ancilla_qubits[0]

    for qubit in controls:
        qc.x(qubit)

    qc.mcx(controls, ancilla)
    qc.z(ancilla)
    qc.mcx(controls, ancilla)

    for qubit in controls:
        qc.x(qubit)
```
