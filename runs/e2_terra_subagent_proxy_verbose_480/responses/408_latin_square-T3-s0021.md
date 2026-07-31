```python
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    a0, a1, a2 = ancilla_qubits[:3]

    # Free cells 0 and 3 must decode to 0, i.e. their two code bits agree.
    qc.cx(problem_qubits[0], a0)
    qc.cx(problem_qubits[1], a0)
    qc.x(a0)

    qc.cx(problem_qubits[6], a1)
    qc.cx(problem_qubits[7], a1)
    qc.x(a1)

    # Free cells 1 and 2 must decode to 2 (low bit 0, high bit 1).
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[4])

    controls = [
        a0,
        problem_qubits[2],
        problem_qubits[3],
        problem_qubits[4],
        problem_qubits[5],
        a1,
    ]

    # Use a clean target prepared in |1> to apply the marked-state phase.
    qc.x(a2)
    qc.mcp(math.pi, controls, a2)
    qc.x(a2)

    qc.x(problem_qubits[4])
    qc.x(problem_qubits[2])

    qc.x(a1)
    qc.cx(problem_qubits[7], a1)
    qc.cx(problem_qubits[6], a1)

    qc.x(a0)
    qc.cx(problem_qubits[1], a0)
    qc.cx(problem_qubits[0], a0)
```
