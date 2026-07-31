```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    from itertools import product

    edges = ((0, 1), (1, 4), (2, 4), (3, 4))

    for bits in product((0, 1), repeat=5):
        if sum(bits) <= 3 and all(bits[u] or bits[v] for u, v in edges):
            for i, bit in enumerate(bits):
                if not bit:
                    qc.x(problem_qubits[i])
            qc.h(problem_qubits[4])
            qc.mcx(problem_qubits[:4], problem_qubits[4])
            qc.h(problem_qubits[4])
            for i, bit in enumerate(bits):
                if not bit:
                    qc.x(problem_qubits[i])
```
