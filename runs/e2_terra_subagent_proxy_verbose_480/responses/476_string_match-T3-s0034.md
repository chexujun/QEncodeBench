```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    matches = ancilla_qubits[:5]

    # Compute the five possible matches of the pattern 0100.
    for offset, match in enumerate(matches):
        zero_controls = [
            problem_qubits[offset],
            problem_qubits[offset + 2],
            problem_qubits[offset + 3],
        ]
        for qubit in zero_controls:
            qc.x(qubit)
        qc.mcx(problem_qubits[offset:offset + 4], match)
        for qubit in reversed(zero_controls):
            qc.x(qubit)

    # Apply -1 to the no-match case. Up to an accepted global phase, this
    # is exactly the phase oracle that marks states having at least one match.
    for match in matches:
        qc.x(match)
    qc.h(matches[-1])
    qc.mcx(matches[:-1], matches[-1])
    qc.h(matches[-1])
    for match in reversed(matches):
        qc.x(match)

    # Uncompute all match indicators.
    for offset in reversed(range(5)):
        match = matches[offset]
        zero_controls = [
            problem_qubits[offset],
            problem_qubits[offset + 2],
            problem_qubits[offset + 3],
        ]
        for qubit in zero_controls:
            qc.x(qubit)
        qc.mcx(problem_qubits[offset:offset + 4], match)
        for qubit in reversed(zero_controls):
            qc.x(qubit)
```
