```python
from math import pi
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    def phase_on(positions: list[int]) -> None:
        zero_positions = [positions[0]]
        for pos in zero_positions:
            qc.x(problem_qubits[pos])

        controls = [problem_qubits[pos] for pos in positions]
        qc.mcp(pi, controls[:-1], controls[-1])

        for pos in reversed(zero_positions):
            qc.x(problem_qubits[pos])

    for offset in range(5):
        phase_on([offset, offset + 1, offset + 2, offset + 3])

    for pos in (0, 4):
        qc.x(problem_qubits[pos])
    controls = [problem_qubits[i] for i in range(8)]
    qc.mcp(pi, controls[:-1], controls[-1])
    for pos in (4, 0):
        qc.x(problem_qubits[pos])
```
