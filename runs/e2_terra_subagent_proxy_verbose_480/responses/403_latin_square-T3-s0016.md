```python
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    # A value is 0 exactly when its two-bit code is 00 or 11.
    eq_a, eq_c, eq_d = ancilla_qubits[:3]

    # Compute whether cells (0,0), (1,2), and (2,1) decode to 0.
    qc.cx(problem_qubits[0], eq_a)
    qc.cx(problem_qubits[1], eq_a)

    qc.cx(problem_qubits[4], eq_c)
    qc.cx(problem_qubits[5], eq_c)

    qc.cx(problem_qubits[6], eq_d)
    qc.cx(problem_qubits[7], eq_d)

    # Convert required zero conditions to one-controls:
    # eq_a = eq_c = eq_d = 0, cell (1,0) code = 01.
    qc.x(eq_a)
    qc.x(eq_c)
    qc.x(eq_d)
    qc.x(problem_qubits[3])

    qc.mcp(
        math.pi,
        [eq_a, eq_c, eq_d, problem_qubits[2]],
        problem_qubits[3],
    )

    qc.x(problem_qubits[3])
    qc.x(eq_d)
    qc.x(eq_c)
    qc.x(eq_a)

    # Uncompute ancillas.
    qc.cx(problem_qubits[7], eq_d)
    qc.cx(problem_qubits[6], eq_d)

    qc.cx(problem_qubits[5], eq_c)
    qc.cx(problem_qubits[4], eq_c)

    qc.cx(problem_qubits[1], eq_a)
    qc.cx(problem_qubits[0], eq_a)
```
