```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    def mark(window: list[int]) -> None:
        zero_positions = (0, 1, 3, 5)
        for i in zero_positions:
            qc.x(window[i])

        target = window[5]
        qc.h(target)
        qc.mcx(window[:5], target)
        qc.h(target)

        for i in reversed(zero_positions):
            qc.x(window[i])

    mark(problem_qubits[0:6])
    mark(problem_qubits[1:7])
```
