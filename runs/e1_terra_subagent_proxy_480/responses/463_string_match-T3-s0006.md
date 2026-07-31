```python
from math import pi

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    flags = ancilla_qubits[:5]

    for start, flag in enumerate(flags):
        window = problem_qubits[start:start + 4]
        for index in (0, 1, 3):
            qc.x(window[index])
        qc.mcx(window, flag)
        for index in (0, 1, 3):
            qc.x(window[index])

    qc.x(flags)
    qc.h(flags[-1])
    qc.mcx(flags[:-1], flags[-1])
    qc.h(flags[-1])
    qc.x(flags)
    qc.global_phase += pi

    for start, flag in reversed(list(enumerate(flags))):
        window = problem_qubits[start:start + 4]
        for index in (0, 1, 3):
            qc.x(window[index])
        qc.mcx(window, flag)
        for index in (0, 1, 3):
            qc.x(window[index])
```
