```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    flags = ancilla_qubits[:5]
    target = ancilla_qubits[5]

    def match(offset: int, flag: int) -> None:
        controls = problem_qubits[offset:offset + 4]
        qc.x(controls[1])
        qc.x(controls[2])
        qc.x(controls[3])
        qc.mcx(controls, flag)
        qc.x(controls[3])
        qc.x(controls[2])
        qc.x(controls[1])

    for offset, flag in enumerate(flags):
        match(offset, flag)

    qc.x(target)
    for flag in flags:
        qc.x(flag)
    qc.mcx(flags, target)
    for flag in reversed(flags):
        qc.x(flag)

    for offset, flag in reversed(list(enumerate(flags))):
        match(offset, flag)
```
