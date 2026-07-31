```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = [(0, 1),(0, 4),(1, 4),(2, 3)]
    for mask in range(32):
        if mask.bit_count() <= 3 and all(((mask >> u) & 1) or ((mask >> v) & 1) for u, v in edges):
            for i, q in enumerate(problem_qubits):
                if not ((mask >> i) & 1): qc.x(q)
            qc.h(problem_qubits[0])
            qc.mcx(problem_qubits[1:], problem_qubits[0])
            qc.h(problem_qubits[0])
            for i, q in enumerate(problem_qubits):
                if not ((mask >> i) & 1): qc.x(q)
```

