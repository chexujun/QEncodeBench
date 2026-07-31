```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    acc = ancilla_qubits[:5]
    phase = ancilla_qubits[5]

    def add_power_of_two(control, shift, inverse=False):
        targets = range(shift, 5) if inverse else range(4, shift - 1, -1)
        for target in targets:
            qc.mcx([control] + acc[shift:target], acc[target])

    terms = ((0, 9), (1, 8), (2, 15), (3, 12), (4, 5))

    for control_index, value in terms:
        for bit in range(5):
            if (value >> bit) & 1:
                add_power_of_two(problem_qubits[control_index], bit)

    for bit, qubit in enumerate(acc):
        if ((23 >> bit) & 1) == 0:
            qc.x(qubit)

    qc.x(phase)
    qc.h(phase)
    qc.mcx(acc, phase)
    qc.h(phase)
    qc.x(phase)

    for bit, qubit in enumerate(acc):
        if ((23 >> bit) & 1) == 0:
            qc.x(qubit)

    for control_index, value in reversed(terms):
        for bit in range(4, -1, -1):
            if (value >> bit) & 1:
                add_power_of_two(problem_qubits[control_index], bit, inverse=True)
```
