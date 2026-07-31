```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    del ancilla_qubits

    # Raw encodings for decoded colors: 0 -> 00 or 11, 1 -> 01, 2 -> 10.
    encodings = {
        0: ((0, 0), (1, 1)),
        1: ((1, 0),),
        2: ((0, 1),),
    }

    def phase_on(bits: tuple[int, ...]) -> None:
        target = problem_qubits[-1]
        controls = problem_qubits[:-1]
        inverted = [q for q, bit in zip(problem_qubits, bits) if bit == 0]

        for q in inverted:
            qc.x(q)
        qc.h(target)
        qc.mcx(controls, target)
        qc.h(target)
        for q in reversed(inverted):
            qc.x(q)

    # Vertices 0, 1, 2 must each differ from vertex 3.
    for center_color in range(3):
        for center_bits in encodings[center_color]:
            leaf_colors = [c for c in range(3) if c != center_color]
            for c0 in leaf_colors:
                for b0 in encodings[c0]:
                    for c1 in leaf_colors:
                        for b1 in encodings[c1]:
                            for c2 in leaf_colors:
                                for b2 in encodings[c2]:
                                    # problem_qubits are ordered [v0_lo, v0_hi, ...].
                                    phase_on(b0 + b1 + b2 + center_bits)
```
