```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = ((0, 1), (0, 2), (1, 2), (2, 3), (2, 4), (3, 4))
    target = problem_qubits[-1]
    controls = list(problem_qubits[:-1])

    for value in range(32):
        bits = [(value >> i) & 1 for i in range(5)]
        if sum(bits) > 3 or any(bits[u] == 0 and bits[v] == 0 for u, v in edges):
            continue

        for i, bit in enumerate(bits):
            if bit == 0:
                qc.x(problem_qubits[i])
        qc.h(target)
        qc.mcx(controls, target)
        qc.h(target)
        for i, bit in enumerate(bits):
            if bit == 0:
                qc.x(problem_qubits[i])
```
