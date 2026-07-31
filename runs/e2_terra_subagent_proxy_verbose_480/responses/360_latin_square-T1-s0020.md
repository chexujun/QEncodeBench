```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # Each free cell must decode to 0.  With the surjective encoding,
    # this is exactly the condition that its two code bits are equal.
    d0, d1, phase_work = ancilla_qubits[:3]
    x0, x1, x2, x3 = problem_qubits

    # Compute inequality flags for the two cells.
    qc.cx(x0, d0)
    qc.cx(x1, d0)
    qc.cx(x2, d1)
    qc.cx(x3, d1)

    # Valid iff both inequality flags are zero.
    qc.x(d0)
    qc.x(d1)

    # CCZ(d0, d1, phase_work), implemented without changing phase_work.
    qc.h(phase_work)
    qc.ccx(d0, d1, phase_work)
    qc.h(phase_work)

    # Uncompute all workspace.
    qc.x(d1)
    qc.x(d0)
    qc.cx(x3, d1)
    qc.cx(x2, d1)
    qc.cx(x1, d0)
    qc.cx(x0, d0)
```
