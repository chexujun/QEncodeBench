```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]
) -> None:
    # Toggle target iff the decoded colors represented by a_bits and b_bits
    # are equal.  Bit pairs are ordered (low_bit, high_bit).
    def decoded_equal(a_bits, b_bits, target):
        color_equal_patterns = (
            ((0, 0), (0, 0)),
            ((0, 0), (1, 1)),
            ((1, 1), (0, 0)),
            ((1, 1), (1, 1)),
            ((1, 0), (1, 0)),
            ((0, 1), (0, 1)),
        )
        controls = [a_bits[0], a_bits[1], b_bits[0], b_bits[1]]

        for a_code, b_code in color_equal_patterns:
            zero_controls = [
                controls[i]
                for i, bit in enumerate(a_code + b_code)
                if bit == 0
            ]
            for qubit in zero_controls:
                qc.x(qubit)
            qc.mcx(controls, target)
            for qubit in reversed(zero_controls):
                qc.x(qubit)

    def vertex_bits(vertex):
        return [
            problem_qubits[2 * vertex],
            problem_qubits[2 * vertex + 1],
        ]

    # The eight constraints are equivalently:
    # 0, 1, 3 are pairwise distinct; 4 has color 3; 2 has color 0.
    # Store violations of these five conditions in the five ancillas.
    reduced_constraints = ((0, 1), (0, 3), (1, 3), (3, 4), (0, 2))
    for ancilla, (u, v) in zip(ancilla_qubits, reduced_constraints):
        decoded_equal(vertex_bits(u), vertex_bits(v), ancilla)

    # Mark exactly when no equality/violation flag is set.
    for ancilla in ancilla_qubits:
        qc.x(ancilla)
    qc.mcp(math.pi, ancilla_qubits[:4], ancilla_qubits[4])
    for ancilla in reversed(ancilla_qubits):
        qc.x(ancilla)

    # Uncompute all flags.
    for ancilla, (u, v) in reversed(list(zip(ancilla_qubits, reduced_constraints))):
        decoded_equal(vertex_bits(u), vertex_bits(v), ancilla)
```
