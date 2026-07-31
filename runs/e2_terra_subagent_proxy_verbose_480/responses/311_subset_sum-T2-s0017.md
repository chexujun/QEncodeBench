```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits
    predicate = ancilla_qubits[0]

    # Compute x1 XOR x3.
    qc.cx(x1, predicate)
    qc.cx(x3, predicate)

    # Phase flip iff x0 = 0, x2 = 0, and predicate = 1.
    qc.x(x0)
    qc.x(x2)
    qc.h(predicate)
    qc.ccx(x0, x2, predicate)
    qc.h(predicate)
    qc.x(x2)
    qc.x(x0)

    # Uncompute the predicate ancilla.
    qc.cx(x3, predicate)
    qc.cx(x1, predicate)
```
