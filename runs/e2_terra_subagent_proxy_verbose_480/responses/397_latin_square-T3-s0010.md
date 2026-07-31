```python
from math import pi

def build_oracle(qc, problem_qubits, ancilla_qubits):
    eq_c = ancilla_qubits[0]
    eq_d = ancilla_qubits[1]

    # Compute XNOR predicates: each ancilla is 1 iff its cell decodes to 0.
    qc.x(eq_c)
    qc.cx(problem_qubits[4], eq_c)
    qc.cx(problem_qubits[5], eq_c)

    qc.x(eq_d)
    qc.cx(problem_qubits[6], eq_d)
    qc.cx(problem_qubits[7], eq_d)

    # Required codes are cell 0 = 10 and cell 1 = 01.
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[3])

    # Phase flip iff all four fixed-bit conditions and both XNORs hold.
    qc.mcp(
        pi,
        [
            problem_qubits[0],
            problem_qubits[1],
            problem_qubits[2],
            problem_qubits[3],
            eq_c,
        ],
        eq_d,
    )

    qc.x(problem_qubits[3])
    qc.x(problem_qubits[0])

    # Uncompute the equality predicates.
    qc.cx(problem_qubits[7], eq_d)
    qc.cx(problem_qubits[6], eq_d)
    qc.x(eq_d)

    qc.cx(problem_qubits[5], eq_c)
    qc.cx(problem_qubits[4], eq_c)
    qc.x(eq_c)
```
