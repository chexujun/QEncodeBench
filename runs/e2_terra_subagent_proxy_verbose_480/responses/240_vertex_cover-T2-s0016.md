```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    x0, x1, x2, x3, x4 = problem_qubits
    xor_03 = ancilla_qubits[0]
    phase_ancilla = ancilla_qubits[1]

    # For a cover of size <= 2, the predicate simplifies to:
    # x1 AND (x0 XOR x3) AND NOT x2 AND NOT x4.
    qc.cx(x0, xor_03)
    qc.cx(x3, xor_03)

    qc.x(x2)
    qc.x(x4)

    # Prepare |-> for phase kickback.
    qc.x(phase_ancilla)
    qc.h(phase_ancilla)
    qc.mcx([x1, xor_03, x2, x4], phase_ancilla)
    qc.h(phase_ancilla)
    qc.x(phase_ancilla)

    qc.x(x4)
    qc.x(x2)

    qc.cx(x3, xor_03)
    qc.cx(x0, xor_03)
```
