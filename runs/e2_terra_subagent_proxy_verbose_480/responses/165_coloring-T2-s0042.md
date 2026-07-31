```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    # One ancilla per edge records whether that edge is monochromatic.
    # The final ancilla is a phase-kickback qubit.
    edges = [(0, 1), (0, 2), (0, 3), (1, 3), (2, 3)]
    violations = ancilla_qubits[:5]
    phase = ancilla_qubits[5]

    def toggle_on_literals(target, literals):
        # literals is [(qubit, required_bit), ...].
        zero_controls = [q for q, bit in literals if bit == 0]
        for q in zero_controls:
            qc.x(q)
        controls = [q for q, _ in literals]
        qc.mcx(controls, target)
        for q in reversed(zero_controls):
            qc.x(q)

    def compute_edge(u, v, target):
        ul, uh = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        vl, vh = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        # Equal decoded colors:
        # color 0: low bits are both 0 (00 and 11 both decode as 0)
        toggle_on_literals(target, [(ul, 0), (vl, 0)])
        # color 1: 01 for both vertices
        toggle_on_literals(target, [(ul, 1), (uh, 0), (vl, 1), (vh, 0)])
        # color 2: 10 for both vertices
        toggle_on_literals(target, [(ul, 0), (uh, 1), (vl, 0), (vh, 1)])

    for (u, v), target in zip(edges, violations):
        compute_edge(u, v, target)

    # Apply -1 exactly when every edge-violation bit is 0.
    qc.x(phase)
    qc.h(phase)
    for q in violations:
        qc.x(q)
    qc.mcx(violations, phase)
    for q in reversed(violations):
        qc.x(q)
    qc.h(phase)
    qc.x(phase)

    # Uncompute every violation bit.
    for (u, v), target in reversed(list(zip(edges, violations))):
        compute_edge(u, v, target)
```
