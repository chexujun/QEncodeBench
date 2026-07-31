```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    match = ancilla_qubits[:5]
    phase_ancilla = ancilla_qubits[5]

    # Compute the five possible substring-match predicates.
    for offset, flag in enumerate(match):
        qc.x(problem_qubits[offset])
        qc.x(problem_qubits[offset + 3])
        qc.mcx(
            [problem_qubits[offset + i] for i in range(4)],
            flag,
        )
        qc.x(problem_qubits[offset + 3])
        qc.x(problem_qubits[offset])

    # Mark the complement (no offset matches). This differs from marking
    # at least one match only by an irrelevant global phase.
    for flag in match:
        qc.x(flag)
    qc.h(phase_ancilla)
    qc.mcx(match, phase_ancilla)
    qc.h(phase_ancilla)
    for flag in reversed(match):
        qc.x(flag)

    # Uncompute all match predicates.
    for offset in reversed(range(5)):
        flag = match[offset]
        qc.x(problem_qubits[offset])
        qc.x(problem_qubits[offset + 3])
        qc.mcx(
            [problem_qubits[offset + i] for i in range(4)],
            flag,
        )
        qc.x(problem_qubits[offset + 3])
        qc.x(problem_qubits[offset])
```
