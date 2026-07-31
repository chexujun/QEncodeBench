```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    matches = ancilla_qubits[:5]

    def toggle_match(offset: int, target: int) -> None:
        controls = problem_qubits[offset:offset + 4]
        qc.x(controls[0])
        qc.x(controls[2])
        qc.mcx(controls, target)
        qc.x(controls[2])
        qc.x(controls[0])

    # Compute whether "0101" matches at each possible offset.
    for offset, target in enumerate(matches):
        toggle_match(offset, target)

    # Phase the state when no offset matches. This differs from phasing all
    # matching states only by an irrelevant global phase.
    for target in matches:
        qc.x(target)
    qc.h(matches[-1])
    qc.mcx(matches[:-1], matches[-1])
    qc.h(matches[-1])
    for target in reversed(matches):
        qc.x(target)

    # Uncompute all match indicators.
    for offset in reversed(range(5)):
        toggle_match(offset, matches[offset])
```
