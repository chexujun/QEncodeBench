```python
from itertools import combinations
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    flags = ancilla_qubits[:5]

    def compute_match(offset: int, target: int) -> None:
        zero_positions = [
            problem_qubits[offset],
            problem_qubits[offset + 1],
            problem_qubits[offset + 2],
        ]
        for qubit in zero_positions:
            qc.x(qubit)
        qc.mcx(problem_qubits[offset : offset + 4], target)
        for qubit in reversed(zero_positions):
            qc.x(qubit)

    for offset, flag in enumerate(flags):
        compute_match(offset, flag)

    for size in range(1, len(flags) + 1):
        for subset in combinations(flags, size):
            if size == 1:
                qc.z(subset[0])
            else:
                qc.h(subset[-1])
                qc.mcx(list(subset[:-1]), subset[-1])
                qc.h(subset[-1])

    for offset, flag in reversed(list(enumerate(flags))):
        compute_match(offset, flag)
```
