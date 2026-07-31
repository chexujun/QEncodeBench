```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    eq0, eq1 = ancilla_qubits[:2]
    x0, x1, x2, x3 = problem_qubits

    # Compute whether each two-bit code has unequal bits.
    qc.cx(x0, eq0)
    qc.cx(x1, eq0)
    qc.cx(x2, eq1)
    qc.cx(x3, eq1)

    # Both cells decode to 0 exactly when both pairs have equal bits.
    qc.x(eq0)
    qc.x(eq1)
    qc.cz(eq0, eq1)
    qc.x(eq1)
    qc.x(eq0)

    # Uncompute all workspace.
    qc.cx(x3, eq1)
    qc.cx(x2, eq1)
    qc.cx(x1, eq0)
    qc.cx(x0, eq0)
```
