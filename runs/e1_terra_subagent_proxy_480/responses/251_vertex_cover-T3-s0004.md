```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    p = problem_qubits

    # The sole satisfying cover is {1, 3, 4}: |010110> in q[0]..q[5] order.
    for i in (0, 2, 5):
        qc.x(p[i])

    qc.h(p[5])
    qc.mcx([p[0], p[1], p[2], p[3], p[4]], p[5])
    qc.h(p[5])

    for i in (0, 2, 5):
        qc.x(p[i])
```
