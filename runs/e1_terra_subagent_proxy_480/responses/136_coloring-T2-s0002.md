```python
from itertools import product
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    valid_states = []
    for colors in product(range(3), repeat=4):
        if all(colors[u] != colors[v] for u, v in ((0, 1), (0, 2), (0, 3), (1, 2), (2, 3))):
            encodings = [((0, 0), (1, 1)) if color == 0 else ((0, 1),) if color == 1 else ((1, 0),) for color in colors]
            for vertex_bits in product(*encodings):
                valid_states.append([bit for bits in vertex_bits for bit in bits])
    target = problem_qubits[-1]
    controls = problem_qubits[:-1]
    for state in valid_states:
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
