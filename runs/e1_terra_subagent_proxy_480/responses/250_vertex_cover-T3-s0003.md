```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    marked_states = (
        (0, 1, 1, 0, 1, 0),  # {1, 2, 4}
        (1, 0, 1, 0, 0, 1),  # {0, 2, 5}
        (1, 1, 1, 0, 0, 0),  # {0, 1, 2}
    )

    target = problem_qubits[5]
    controls = problem_qubits[:5]

    for state in marked_states:
        for qubit, bit in zip(problem_qubits, state):
            if bit == 0:
                qc.x(qubit)

        qc.h(target)
        qc.mcx(controls, target)
        qc.h(target)

        for qubit, bit in zip(problem_qubits, state):
            if bit == 0:
                qc.x(qubit)
```
