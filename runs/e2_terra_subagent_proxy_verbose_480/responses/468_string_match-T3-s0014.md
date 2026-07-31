```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    matches = ancilla_qubits[:5]

    # Compute the five possible matches of pattern 0111.
    for offset, target in enumerate(matches):
        controls = [problem_qubits[offset + i] for i in range(4)]
        qc.x(controls[0])
        qc.mcx(controls, target)
        qc.x(controls[0])

    # Distinct matches cannot overlap; only offsets 0 and 4 can both match.
    # The CZ corrects the phase when both disjoint occurrences are present.
    for target in matches:
        qc.z(target)
    qc.cz(matches[0], matches[4])

    # Uncompute all match indicators.
    for offset in reversed(range(5)):
        target = matches[offset]
        controls = [problem_qubits[offset + i] for i in range(4)]
        qc.x(controls[0])
        qc.mcx(controls, target)
        qc.x(controls[0])
```
