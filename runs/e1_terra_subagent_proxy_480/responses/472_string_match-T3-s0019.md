```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    flags = ancilla_qubits[:5]
    output = ancilla_qubits[5]

    for i, flag in enumerate(flags):
        qc.x(problem_qubits[i + 1])
        qc.mcx(
            [problem_qubits[i], problem_qubits[i + 1], problem_qubits[i + 2]],
            flag,
        )
        qc.x(problem_qubits[i + 1])

    qc.x(output)
    for flag in flags:
        qc.x(flag)
    qc.mcx(flags, output)
    for flag in flags:
        qc.x(flag)
    qc.z(output)

    for flag in reversed(flags):
        i = flags.index(flag)
        qc.x(problem_qubits[i + 1])
        qc.mcx(
            [problem_qubits[i], problem_qubits[i + 1], problem_qubits[i + 2]],
            flag,
        )
        qc.x(problem_qubits[i + 1])
```
