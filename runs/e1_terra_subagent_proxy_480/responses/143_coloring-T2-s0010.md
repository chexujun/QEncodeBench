```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = [(0, 2), (1, 2), (1, 3), (1, 4), (2, 4)]
    flags = ancilla_qubits[:5]
    phase_ancilla = ancilla_qubits[5]
    equal_patterns = [((0,0),(0,0)), ((0,0),(1,1)), ((1,1),(0,0)), ((1,1),(1,1)), ((1,0),(1,0)), ((0,1),(0,1))]
    def toggle_on_pattern(controls, bits, target):
        for qubit, bit in zip(controls, bits):
            if bit == 0: qc.x(qubit)
        qc.mcx(controls, target)
        for qubit, bit in zip(controls, bits):
            if bit == 0: qc.x(qubit)
    def compute_equalities():
        for (u,v), flag in zip(edges, flags):
            controls=[problem_qubits[2*u],problem_qubits[2*u+1],problem_qubits[2*v],problem_qubits[2*v+1]]
            for pu,pv in equal_patterns: toggle_on_pattern(controls,pu+pv,flag)
    compute_equalities()
    for flag in flags: qc.x(flag)
    qc.mcx(flags,phase_ancilla); qc.z(phase_ancilla); qc.mcx(flags,phase_ancilla)
    for flag in flags: qc.x(flag)
    compute_equalities()
```
