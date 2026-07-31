```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    flags = ancilla_qubits[:5]
    work = ancilla_qubits[5]
    edges = [(0, 1), (0, 2), (1, 2), (1, 3), (1, 4)]

    def toggle_pattern(controls, target, pattern):
        for qubit, bit in zip(controls, pattern):
            if bit == 0:
                qc.x(qubit)
        qc.mcx(controls, target)
        for qubit, bit in zip(reversed(controls), reversed(pattern)):
            if bit == 0:
                qc.x(qubit)

    # Compute one flag per edge.  A flag is 1 exactly when its endpoints
    # decode to the same color.
    for flag, (u, v) in zip(flags, edges):
        ul, uh = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        vl, vh = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        # work = low(u) XOR high(u).
        # It is 0 precisely for the two encodings of color 0.
        qc.cx(ul, work)
        qc.cx(uh, work)

        # Both endpoints decode to color 0.
        toggle_pattern([work, vl, vh], flag, [0, 0, 0])
        toggle_pattern([work, vl, vh], flag, [0, 1, 1])

        # Both endpoints decode to color 1 or both decode to color 2.
        toggle_pattern([work, uh, vl, vh], flag, [1, 0, 1, 0])
        toggle_pattern([work, uh, vl, vh], flag, [1, 1, 0, 1])

        qc.cx(uh, work)
        qc.cx(ul, work)

    # Mark exactly the states with no monochromatic edge.
    for flag in flags:
        qc.x(flag)
    qc.x(work)
    qc.h(work)
    qc.mcx(flags, work)
    qc.h(work)
    qc.x(work)
    for flag in reversed(flags):
        qc.x(flag)

    # Uncompute all edge-violation flags.
    for flag, (u, v) in zip(reversed(flags), reversed(edges)):
        ul, uh = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        vl, vh = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        qc.cx(ul, work)
        qc.cx(uh, work)

        toggle_pattern([work, uh, vl, vh], flag, [1, 1, 0, 1])
        toggle_pattern([work, uh, vl, vh], flag, [1, 0, 1, 0])
        toggle_pattern([work, vl, vh], flag, [0, 1, 1])
        toggle_pattern([work, vl, vh], flag, [0, 0, 0])

        qc.cx(uh, work)
        qc.cx(ul, work)
```
