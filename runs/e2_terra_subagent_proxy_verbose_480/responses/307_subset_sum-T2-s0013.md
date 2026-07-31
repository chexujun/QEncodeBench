```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    x0, x1, x2, x3 = problem_qubits
    parity, both_required, marked = ancilla_qubits[:3]

    # Sum 22 iff x1 = x3 = 1 and exactly one of x0, x2 is selected.
    qc.cx(x0, parity)
    qc.cx(x2, parity)
    qc.ccx(x1, x3, both_required)
    qc.ccx(parity, both_required, marked)

    qc.z(marked)

    qc.ccx(parity, both_required, marked)
    qc.ccx(x1, x3, both_required)
    qc.cx(x2, parity)
    qc.cx(x0, parity)
```
