```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = [(0, 2), (0, 4), (1, 3), (1, 4), (2, 3), (3, 4)]
    flags = ancilla_qubits[:6]
    marker = ancilla_qubits[6]
    color_states = (((0, 0), (1, 1)), ((0, 1),), ((1, 0),))
    def toggle_if_state(qubits, bits, target):
        zeros = [q for q, bit in zip(qubits, bits) if bit == 0]
        for q in zeros: qc.x(q)
        qc.mcx(qubits, target)
        for q in reversed(zeros): qc.x(q)
    def compute_conflicts():
        for (u, v), flag in zip(edges, flags):
            uq = [problem_qubits[2*u], problem_qubits[2*u+1]]
            vq = [problem_qubits[2*v], problem_qubits[2*v+1]]
            for states in color_states:
                for us in states:
                    for vs in states: toggle_if_state(uq + vq, us + vs, flag)
    compute_conflicts()
    for flag in flags: qc.x(flag)
    qc.mcx(flags, marker); qc.z(marker); qc.mcx(flags, marker)
    for flag in reversed(flags): qc.x(flag)
    compute_conflicts()
```
