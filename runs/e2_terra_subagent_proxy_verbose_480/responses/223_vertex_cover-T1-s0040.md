```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits
    edge01, edge13, edge23, weight_ge_3, flag = ancilla_qubits[:5]

    # Compute whether each edge is covered: a OR b = a XOR b XOR (a AND b).
    qc.cx(x0, edge01)
    qc.cx(x1, edge01)
    qc.ccx(x0, x1, edge01)

    qc.cx(x1, edge13)
    qc.cx(x3, edge13)
    qc.ccx(x1, x3, edge13)

    qc.cx(x2, edge23)
    qc.cx(x3, edge23)
    qc.ccx(x2, x3, edge23)

    # Compute weight_ge_3 using its algebraic normal form.
    qc.mcx([x0, x1, x2], weight_ge_3)
    qc.mcx([x0, x1, x3], weight_ge_3)
    qc.mcx([x0, x2, x3], weight_ge_3)
    qc.mcx([x1, x2, x3], weight_ge_3)
    qc.mcx([x0, x1, x2, x3], weight_ge_3)

    # flag = all edges covered AND weight < 3.
    qc.x(weight_ge_3)
    qc.mcx([edge01, edge13, edge23, weight_ge_3], flag)
    qc.z(flag)
    qc.mcx([edge01, edge13, edge23, weight_ge_3], flag)
    qc.x(weight_ge_3)

    # Uncompute the weight predicate.
    qc.mcx([x0, x1, x2, x3], weight_ge_3)
    qc.mcx([x1, x2, x3], weight_ge_3)
    qc.mcx([x0, x2, x3], weight_ge_3)
    qc.mcx([x0, x1, x3], weight_ge_3)
    qc.mcx([x0, x1, x2], weight_ge_3)

    # Uncompute the edge predicates.
    qc.ccx(x2, x3, edge23)
    qc.cx(x3, edge23)
    qc.cx(x2, edge23)

    qc.ccx(x1, x3, edge13)
    qc.cx(x3, edge13)
    qc.cx(x1, edge13)

    qc.ccx(x0, x1, edge01)
    qc.cx(x1, edge01)
    qc.cx(x0, edge01)
```
