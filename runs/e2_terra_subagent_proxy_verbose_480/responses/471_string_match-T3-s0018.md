```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    matches = ancilla_qubits[:5]
    no_match = ancilla_qubits[5]

    # Compute the five possible matches of the pattern "1000".
    for offset, match in enumerate(matches):
        zero_bits = [problem_qubits[offset + i] for i in (1, 2, 3)]
        for qubit in zero_bits:
            qc.x(qubit)
        qc.mcx(
            [problem_qubits[offset + i] for i in range(4)],
            match,
        )
        for qubit in reversed(zero_bits):
            qc.x(qubit)

    # no_match = NOT (matches[0] OR ... OR matches[4]).
    for match in matches:
        qc.x(match)
    qc.mcx(matches, no_match)
    for match in reversed(matches):
        qc.x(match)

    # This phases non-matches by -1, which differs from phasing matches
    # by -1 only by an irrelevant global phase.
    qc.z(no_match)

    # Uncompute no_match.
    for match in matches:
        qc.x(match)
    qc.mcx(matches, no_match)
    for match in reversed(matches):
        qc.x(match)

    # Uncompute all window-match ancillas.
    for offset in reversed(range(5)):
        match = matches[offset]
        zero_bits = [problem_qubits[offset + i] for i in (1, 2, 3)]
        for qubit in zero_bits:
            qc.x(qubit)
        qc.mcx(
            [problem_qubits[offset + i] for i in range(4)],
            match,
        )
        for qubit in reversed(zero_bits):
            qc.x(qubit)
```
