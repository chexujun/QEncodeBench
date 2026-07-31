```python
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    x0, x1, x2, x3, x4 = problem_qubits
    parity = ancilla_qubits[0]

    # With a cover size of at most 2, vertex 1 must be selected.
    # Then exactly one of vertices 2 and 3 must be selected; 0 and 4
    # must be unselected.
    qc.cx(x2, parity)
    qc.cx(x3, parity)

    qc.x(x0)
    qc.x(x4)
    qc.mcp(math.pi, [x1, parity, x0, x4])
    qc.x(x4)
    qc.x(x0)

    qc.cx(x3, parity)
    qc.cx(x2, parity)
```
