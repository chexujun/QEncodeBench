```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    match = ancilla_qubits[:5]
    found = ancilla_qubits[5]

    controls = [
        [problem_qubits[o], problem_qubits[o + 2], problem_qubits[o + 3]]
        for o in range(5)
    ]

    # Compute the five offset-match predicates.
    for flag, bits in zip(match, controls):
        for q in bits:
            qc.x(q)
        qc.mcx(bits, flag)
        for q in reversed(bits):
            qc.x(q)

    # Compute found = OR(match[0], ..., match[4]).
    for flag in match:
        qc.x(flag)
    qc.mcx(match, found)
    qc.x(found)
    for flag in reversed(match):
        qc.x(flag)

    qc.z(found)

    # Uncompute found.
    for flag in match:
        qc.x(flag)
    qc.x(found)
    qc.mcx(match, found)
    for flag in reversed(match):
        qc.x(flag)

    # Uncompute the offset-match predicates.
    for flag, bits in reversed(list(zip(match, controls))):
        for q in bits:
            qc.x(q)
        qc.mcx(bits, flag)
        for q in reversed(bits):
            qc.x(q)
```
