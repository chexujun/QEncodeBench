```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    a0, a1, a2, phase_ancilla = ancilla_qubits

    def compute_equal(v1, v2, target):
        l1, h1 = problem_qubits[2 * v1], problem_qubits[2 * v1 + 1]
        l2, h2 = problem_qubits[2 * v2], problem_qubits[2 * v2 + 1]

        # Store bitwise differences in the second vertex's wires.
        qc.cx(l1, l2)
        qc.cx(h1, h2)

        # Equal codes: differences are 00.
        qc.x(l2)
        qc.x(h2)
        qc.ccx(l2, h2, target)
        qc.x(h2)
        qc.x(l2)

        # Complementary codes decode equally precisely for 00 <-> 11.
        qc.x(l1)
        qc.x(h1)
        qc.mcx([l2, h2, l1, h1], target)
        qc.x(h1)
        qc.x(l1)

        qc.mcx([l2, h2, l1, h1], target)

        # Restore the input encoding.
        qc.cx(h1, h2)
        qc.cx(l1, l2)

    # Equality flags for edges (0,2), (1,3), and (2,3).
    compute_equal(0, 2, a0)
    compute_equal(1, 3, a1)
    compute_equal(2, 3, a2)

    # Mark iff no edge is monochromatic.
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.mcx([a0, a1, a2], phase_ancilla)
    qc.z(phase_ancilla)
    qc.mcx([a0, a1, a2], phase_ancilla)
    qc.x(a2)
    qc.x(a1)
    qc.x(a0)

    compute_equal(2, 3, a2)
    compute_equal(1, 3, a1)
    compute_equal(0, 2, a0)
```
