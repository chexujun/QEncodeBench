```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    x0, x1, x2, x3 = problem_qubits
    e03, e12, e23, s0, s1, s2 = ancilla_qubits

    # Compute whether each edge is covered.
    for u, v, edge_flag in ((x0, x3, e03), (x1, x2, e12), (x2, x3, e23)):
        qc.cx(u, edge_flag)
        qc.cx(v, edge_flag)
        qc.ccx(u, v, edge_flag)

    # Reversibly accumulate the Hamming weight into s0, s1, s2.
    for vertex in problem_qubits:
        qc.mcx([vertex, s0, s1], s2)
        qc.ccx(vertex, s0, s1)
        qc.cx(vertex, s0)

    # Apply a phase when every edge is covered and the weight is 0, 1, or 2.
    def phase_if_weight_is(value):
        bits = ((value >> 0) & 1, (value >> 1) & 1, (value >> 2) & 1)
        for bit, qubit in zip(bits, (s0, s1, s2)):
            if bit == 0:
                qc.x(qubit)

        qc.h(e23)
        qc.mcx([e03, e12, s0, s1, s2], e23)
        qc.h(e23)

        for bit, qubit in zip(bits, (s0, s1, s2)):
            if bit == 0:
                qc.x(qubit)

    phase_if_weight_is(0)
    phase_if_weight_is(1)
    phase_if_weight_is(2)

    # Uncompute the Hamming weight.
    for vertex in reversed(problem_qubits):
        qc.cx(vertex, s0)
        qc.ccx(vertex, s0, s1)
        qc.mcx([vertex, s0, s1], s2)

    # Uncompute edge-coverage flags.
    for u, v, edge_flag in reversed(((x0, x3, e03), (x1, x2, e12), (x2, x3, e23))):
        qc.ccx(u, v, edge_flag)
        qc.cx(v, edge_flag)
        qc.cx(u, edge_flag)
```
