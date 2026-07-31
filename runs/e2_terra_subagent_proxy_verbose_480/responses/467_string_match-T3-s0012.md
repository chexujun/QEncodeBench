```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    matches = ancilla_qubits[:5]
    flag = ancilla_qubits[5]

    def toggle_match(offset: int, target: int) -> None:
        controls = problem_qubits[offset:offset + 4]
        for qubit in controls[:3]:
            qc.x(qubit)
        qc.mcx(controls, target)
        for qubit in reversed(controls[:3]):
            qc.x(qubit)

    # Compute the five possible substring matches.
    for offset, target in enumerate(matches):
        toggle_match(offset, target)

    # Compute flag = OR(matches).
    qc.x(flag)
    for qubit in matches:
        qc.x(qubit)
    qc.mcx(matches, flag)
    for qubit in reversed(matches):
        qc.x(qubit)

    qc.z(flag)

    # Uncompute the OR flag.
    for qubit in matches:
        qc.x(qubit)
    qc.mcx(matches, flag)
    for qubit in reversed(matches):
        qc.x(qubit)
    qc.x(flag)

    # Uncompute the substring matches.
    for offset in reversed(range(5)):
        toggle_match(offset, matches[offset])
```
