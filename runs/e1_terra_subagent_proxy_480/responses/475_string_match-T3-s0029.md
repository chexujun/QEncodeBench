```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    flags = ancilla_qubits[:5]

    for offset, flag in enumerate(flags):
        q1 = problem_qubits[offset]
        q0a = problem_qubits[offset + 2]
        q0b = problem_qubits[offset + 3]
        qc.x(q0a)
        qc.x(q0b)
        qc.mcx([q1, q0a, q0b], flag)
        qc.x(q0b)
        qc.x(q0a)

    qc.x(flags)
    qc.h(flags[-1])
    qc.mcx(flags[:-1], flags[-1])
    qc.h(flags[-1])
    qc.x(flags)
    qc.global_phase += 3.141592653589793

    for offset, flag in reversed(list(enumerate(flags))):
        q1 = problem_qubits[offset]
        q0a = problem_qubits[offset + 2]
        q0b = problem_qubits[offset + 3]
        qc.x(q0a)
        qc.x(q0b)
        qc.mcx([q1, q0a, q0b], flag)
        qc.x(q0b)
        qc.x(q0a)
```
