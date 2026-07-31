```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    flags = ancilla_qubits[:5]

    for i, flag in enumerate(flags):
        qc.ccx(problem_qubits[i], problem_qubits[i + 1], flag)
        qc.ccx(flag, problem_qubits[i + 2], flag)

    qc.x(flags)
    qc.h(flags[-1])
    qc.mcx(flags[:-1], flags[-1])
    qc.h(flags[-1])
    qc.x(flags)

    for i, flag in reversed(list(enumerate(flags))):
        qc.ccx(flag, problem_qubits[i + 2], flag)
        qc.ccx(problem_qubits[i], problem_qubits[i + 1], flag)
```
