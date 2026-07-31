```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    low = [problem_qubits[2 * v] for v in range(5)]
    tag = [problem_qubits[2 * v + 1] for v in range(5)]

    # Replace each high bit by low XOR high.  tag==0 denotes color 0;
    # tag==1 denotes colors 1 or 2, distinguished by low.
    for lo, hi in zip(low, tag):
        qc.cx(lo, hi)

    # Vertex 0 is color 0.  Then vertices 1 and 2 are the two
    # nonzero colors, while vertices 3 and 4 are color 0.
    qc.cx(low[1], low[2])
    qc.x([tag[0], tag[3], tag[4]])
    qc.mcp(math.pi, tag, low[2])
    qc.x([tag[0], tag[3], tag[4]])
    qc.cx(low[1], low[2])

    # Vertex 0 is nonzero.  Exactly one of vertices 1 and 2 is color 0;
    # the other is the opposite nonzero color.  Vertices 3 and 4 match
    # vertex 0.
    for target, zero_tag in ((low[2], tag[1]), (low[1], tag[2])):
        qc.cx(low[0], target)
        qc.cx(low[0], low[3])
        qc.cx(low[0], low[4])
        qc.x([zero_tag, low[3], low[4]])
        qc.mcp(math.pi, tag + [low[3], low[4]], target)
        qc.x([zero_tag, low[3], low[4]])
        qc.cx(low[0], low[4])
        qc.cx(low[0], low[3])
        qc.cx(low[0], target)

    for lo, hi in reversed(list(zip(low, tag))):
        qc.cx(lo, hi)
```
