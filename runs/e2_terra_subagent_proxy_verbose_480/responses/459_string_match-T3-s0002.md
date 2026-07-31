```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    flags = ancilla_qubits[:5]
    result = ancilla_qubits[5]

    # Compute whether "0011" begins at each offset 0..4.
    for offset, flag in enumerate(flags):
        qc.x(problem_qubits[offset])
        qc.x(problem_qubits[offset + 1])
        qc.mcx(problem_qubits[offset:offset + 4], flag)
        qc.x(problem_qubits[offset + 1])
        qc.x(problem_qubits[offset])

    # result = OR(flags), using a zero-controlled MCX.
    qc.x(result)
    for flag in flags:
        qc.x(flag)
    qc.mcx(flags, result)
    for flag in reversed(flags):
        qc.x(flag)

    qc.z(result)

    # Uncompute result.
    for flag in flags:
        qc.x(flag)
    qc.mcx(flags, result)
    for flag in reversed(flags):
        qc.x(flag)
    qc.x(result)

    # Uncompute match flags.
    for offset, flag in reversed(list(enumerate(flags))):
        qc.x(problem_qubits[offset])
        qc.x(problem_qubits[offset + 1])
        qc.mcx(problem_qubits[offset:offset + 4], flag)
        qc.x(problem_qubits[offset + 1])
        qc.x(problem_qubits[offset])
```
