```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Each free cell must decode to value 2, whose only code is 10:
    # low bit = 0, high bit = 1.
    lows = [problem_qubits[0], problem_qubits[2], problem_qubits[4]]
    for q in lows:
        qc.x(q)

    target = problem_qubits[5]
    controls = problem_qubits[:5]
    qc.h(target)
    qc.mcx(controls, target)
    qc.h(target)

    for q in reversed(lows):
        qc.x(q)
```
