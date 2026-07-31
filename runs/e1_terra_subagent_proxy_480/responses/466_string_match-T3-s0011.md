```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    flags = ancilla_qubits[:5]
    pattern = "1001"

    for offset, flag in enumerate(flags):
        for j, bit in enumerate(pattern):
            if bit == "0":
                qc.x(problem_qubits[offset + j])
        qc.mcx(
            [problem_qubits[offset + j] for j in range(4)],
            flag,
        )
        for j, bit in enumerate(pattern):
            if bit == "0":
                qc.x(problem_qubits[offset + j])

    for flag in flags:
        qc.x(flag)
    qc.h(flags[-1])
    qc.mcx(flags[:-1], flags[-1])
    qc.h(flags[-1])
    for flag in flags:
        qc.x(flag)

    for offset, flag in reversed(list(enumerate(flags))):
        for j, bit in enumerate(pattern):
            if bit == "0":
                qc.x(problem_qubits[offset + j])
        qc.mcx(
            [problem_qubits[offset + j] for j in range(4)],
            flag,
        )
        for j, bit in enumerate(pattern):
            if bit == "0":
                qc.x(problem_qubits[offset + j])
```
