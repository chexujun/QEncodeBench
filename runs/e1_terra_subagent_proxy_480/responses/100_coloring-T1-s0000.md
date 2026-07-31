```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    p = problem_qubits
    flags = ancilla_qubits[:4]
    work = ancilla_qubits[4]
    edges = ((0, 2), (1, 2), (1, 3), (2, 3))
    equal_patterns = ("0000", "0011", "1100", "1111", "0101", "1010")
    for flag, (u, v) in zip(flags, edges):
        controls = [p[2 * u], p[2 * u + 1], p[2 * v], p[2 * v + 1]]
        for pattern in equal_patterns: qc.mcx(controls, flag, ctrl_state=pattern)
    for flag in flags: qc.x(flag)
    qc.h(work); qc.mcx(flags, work); qc.h(work)
    for flag in flags: qc.x(flag)
    for flag, (u, v) in reversed(list(zip(flags, edges))):
        controls = [p[2 * u], p[2 * u + 1], p[2 * v], p[2 * v + 1]]
        for pattern in reversed(equal_patterns): qc.mcx(controls, flag, ctrl_state=pattern)
```
