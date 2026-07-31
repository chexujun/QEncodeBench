```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    from itertools import product
    from math import pi

    edges = ((0, 1), (0, 2), (0, 4), (1, 3),
             (2, 3), (2, 4), (3, 4))
    encodings = {
        0: ((0, 0), (1, 1)),
        1: ((0, 1),),
        2: ((1, 0),),
    }

    controls = problem_qubits[:-1]
    target = problem_qubits[-1]

    for colors in product(range(3), repeat=5):
        if any(colors[u] == colors[v] for u, v in edges):
            continue
        for codes in product(*(encodings[c] for c in colors)):
            bits = [bit for code in codes for bit in code]
            flipped = [q for q, bit in zip(problem_qubits, bits) if bit == 0]
            for q in flipped:
                qc.x(q)
            qc.mcp(pi, controls, target)
            for q in reversed(flipped):
                qc.x(q)
```
