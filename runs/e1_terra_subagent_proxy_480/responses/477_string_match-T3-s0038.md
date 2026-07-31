```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    target = ancilla_qubits[0]

    if len(ancilla_qubits) >= 6:
        work = ancilla_qubits[1:6]

        for offset, flag in enumerate(work):
            controls = problem_qubits[offset:offset + 4]
            qc.x(controls[2])
            qc.mcx(controls, flag)
            qc.x(controls[2])

        qc.x(work)
        qc.mcx(work, target)
        qc.x(work)

        for offset, flag in reversed(list(enumerate(work))):
            controls = problem_qubits[offset:offset + 4]
            qc.x(controls[2])
            qc.mcx(controls, flag)
            qc.x(controls[2])
    else:
        for value in range(256):
            bits = [(value >> (7 - i)) & 1 for i in range(8)]
            if any(bits[i:i + 4] == [1, 1, 0, 1] for i in range(5)):
                zeros = [problem_qubits[i] for i, bit in enumerate(bits) if bit == 0]
                qc.x(zeros)
                qc.mcx(problem_qubits, target)
                qc.x(zeros)
```
