```python
from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    matches = ancilla_qubits[:5]
    phase_target = ancilla_qubits[5]

    # Compute whether each of the five length-4 windows is 1111.
    for offset, match in enumerate(matches):
        qc.mcx(problem_qubits[offset:offset + 4], match)

    # Phase the unique non-matching case (all match flags are zero).
    # This differs from phasing the OR by only an irrelevant global phase.
    for match in matches:
        qc.x(match)
    qc.x(phase_target)
    qc.mcp(math.pi, matches, phase_target)
    qc.x(phase_target)
    for match in reversed(matches):
        qc.x(match)

    # Uncompute the match flags.
    for offset in reversed(range(5)):
        qc.mcx(problem_qubits[offset:offset + 4], matches[offset])
```
