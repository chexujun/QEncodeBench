```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    match_ancillas = ancilla_qubits[:3]

    # Compute whether "1011" occurs at offsets 0, 1, or 2.
    for offset, target in enumerate(match_ancillas):
        # The second pattern bit is 0, so convert it into a positive control.
        qc.x(problem_qubits[offset + 1])
        qc.mcx(
            [
                problem_qubits[offset],
                problem_qubits[offset + 1],
                problem_qubits[offset + 2],
                problem_qubits[offset + 3],
            ],
            target,
        )
        qc.x(problem_qubits[offset + 1])

    # Apply a phase to the all-zero match flag state.  This differs from the
    # desired OR phase oracle only by an irrelevant global phase.
    for a in match_ancillas:
        qc.x(a)
    qc.h(match_ancillas[2])
    qc.ccx(match_ancillas[0], match_ancillas[1], match_ancillas[2])
    qc.h(match_ancillas[2])
    for a in reversed(match_ancillas):
        qc.x(a)

    # Uncompute match flags.
    for offset, target in reversed(list(enumerate(match_ancillas))):
        qc.x(problem_qubits[offset + 1])
        qc.mcx(
            [
                problem_qubits[offset],
                problem_qubits[offset + 1],
                problem_qubits[offset + 2],
                problem_qubits[offset + 3],
            ],
            target,
        )
        qc.x(problem_qubits[offset + 1])
```
