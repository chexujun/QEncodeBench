```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits
    bad = ancilla_qubits[0]

    # bad = (x0 & x1) XOR (x0 & x2) XOR (x1 & x2).
    # For three leaf vertices, this is 1 exactly when at least two
    # leaves are selected.
    qc.ccx(x0, x1, bad)
    qc.ccx(x0, x2, bad)
    qc.ccx(x1, x2, bad)

    # A valid cover of size <= 2 requires x3 = 1 and bad = 0.
    qc.x(bad)
    qc.cz(x3, bad)
    qc.x(bad)

    # Uncompute ancilla.
    qc.ccx(x1, x2, bad)
    qc.ccx(x0, x2, bad)
    qc.ccx(x0, x1, bad)
```
