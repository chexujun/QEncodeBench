```python
from itertools import combinations
from math import pi
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    matches = ancilla_qubits[:5]

    for offset, match_qubit in enumerate(matches):
        zero_bits = [problem_qubits[offset], problem_qubits[offset + 2]]
        for qubit in zero_bits:
            qc.x(qubit)
        qc.mcx(problem_qubits[offset:offset + 4], match_qubit)
        for qubit in reversed(zero_bits):
            qc.x(qubit)

    for size in range(1, len(matches) + 1):
        for subset in combinations(matches, size):
            if size == 1:
                qc.z(subset[0])
            else:
                qc.mcp(pi, list(subset[:-1]), subset[-1])

    for offset, match_qubit in reversed(list(enumerate(matches))):
        zero_bits = [problem_qubits[offset], problem_qubits[offset + 2]]
        for qubit in zero_bits:
            qc.x(qubit)
        qc.mcx(problem_qubits[offset:offset + 4], match_qubit)
        for qubit in reversed(zero_bits):
            qc.x(qubit)
```
