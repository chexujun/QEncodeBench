```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    def mark_offset(offset: int) -> None:
        target = problem_qubits[offset]
        zero_positions = [offset + 1, offset + 3, offset + 5]

        for pos in zero_positions:
            qc.x(problem_qubits[pos])

        qc.h(target)
        qc.mcx([problem_qubits[offset + i] for i in range(1, 6)], target)
        qc.h(target)

        for pos in reversed(zero_positions):
            qc.x(problem_qubits[pos])

    mark_offset(0)
    mark_offset(1)
```
