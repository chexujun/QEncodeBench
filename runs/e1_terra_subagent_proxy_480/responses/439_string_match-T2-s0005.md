```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    flags = ancilla_qubits[:3]

    for offset, flag in enumerate(flags):
        qc.x(problem_qubits[offset + 1])
        qc.mcx(problem_qubits[offset : offset + 4], flag)
        qc.x(problem_qubits[offset + 1])

    for flag in flags:
        qc.z(flag)
    qc.cz(flags[0], flags[1])
    qc.cz(flags[0], flags[2])
    qc.cz(flags[1], flags[2])
    qc.ccz(flags[0], flags[1], flags[2])

    for offset, flag in reversed(list(enumerate(flags))):
        qc.x(problem_qubits[offset + 1])
        qc.mcx(problem_qubits[offset : offset + 4], flag)
        qc.x(problem_qubits[offset + 1])
```
