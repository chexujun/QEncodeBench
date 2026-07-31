```python
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    a0, a1, b0, b1, c0, c1 = problem_qubits
    parity = ancilla_qubits[0]
    phase_target = ancilla_qubits[1]

    # Decode b as 0 iff its two-bit code is 00 or 11.
    qc.cx(b0, parity)
    qc.cx(b1, parity)

    # Convert required zero-valued controls to positive controls.
    qc.x(a1)
    qc.x(parity)
    qc.x(c1)

    # Kick back a phase iff a=1, b=0, and c=1.
    qc.x(phase_target)
    qc.mcp(math.pi, [a0, a1, parity, c0, c1], phase_target)
    qc.x(phase_target)

    # Uncompute all temporary changes.
    qc.x(c1)
    qc.x(parity)
    qc.x(a1)
    qc.cx(b1, parity)
    qc.cx(b0, parity)
```
