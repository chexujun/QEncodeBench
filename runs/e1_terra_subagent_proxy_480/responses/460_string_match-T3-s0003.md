```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    flags = ancilla_qubits[:5]

    for offset, flag in enumerate(flags):
        window = problem_qubits[offset:offset + 4]
        qc.x(window)
        qc.mcx(window, flag)
        qc.x(window)

    qc.global_phase += 3.141592653589793
    qc.x(flags)
    qc.h(flags[-1])
    qc.mcx(flags[:-1], flags[-1])
    qc.h(flags[-1])
    qc.x(flags)

    for offset, flag in reversed(list(enumerate(flags))):
        window = problem_qubits[offset:offset + 4]
        qc.x(window)
        qc.mcx(window, flag)
        qc.x(window)
```
