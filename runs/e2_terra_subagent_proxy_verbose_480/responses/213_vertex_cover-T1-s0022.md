```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    x0, x1, x2, x3 = problem_qubits
    e02, e03, e13 = ancilla_qubits[:3]

    # Compute whether each edge is covered: a = u OR v.
    qc.cx(x0, e02)
    qc.cx(x2, e02)
    qc.ccx(x0, x2, e02)

    qc.cx(x0, e03)
    qc.cx(x3, e03)
    qc.ccx(x0, x3, e03)

    qc.cx(x1, e13)
    qc.cx(x3, e13)
    qc.ccx(x1, x3, e13)

    # Phase for all edges covered.
    qc.mcp(math.pi, [e02, e03], e13)

    # Cancel that phase when the cover has at least three vertices.
    # The Boolean condition weight(x) >= 3 is the XOR of its four
    # triple-products and the four-bit product.
    qc.mcp(math.pi, [e02, e03, e13, x0, x1], x2)
    qc.mcp(math.pi, [e02, e03, e13, x0, x1], x3)
    qc.mcp(math.pi, [e02, e03, e13, x0, x2], x3)
    qc.mcp(math.pi, [e02, e03, e13, x1, x2], x3)
    qc.mcp(math.pi, [e02, e03, e13, x0, x1, x2], x3)

    # Uncompute edge-coverage ancillas.
    qc.ccx(x0, x3, e03)
    qc.cx(x3, e03)
    qc.cx(x0, e03)

    qc.ccx(x1, x3, e13)
    qc.cx(x3, e13)
    qc.cx(x1, e13)

    qc.ccx(x0, x2, e02)
    qc.cx(x2, e02)
    qc.cx(x0, e02)
```
