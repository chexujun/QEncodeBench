```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    colors = []
    for c0 in range(3):
        for c3 in range(3):
            for c4 in range(3):
                if len({c0, c3, c4}) != 3:
                    continue
                c1 = c0
                c2 = c4
                colors.append((c0, c1, c2, c3, c4))

    encodings = {
        0: ((0, 0), (1, 1)),
        1: ((1, 0),),
        2: ((0, 1),),
    }

    target = problem_qubits[-1]
    controls = problem_qubits[:-1]

    for assignment in colors:
        bitstrings = [[]]
        for color in assignment:
            bitstrings = [
                prefix + [b0, b1]
                for prefix in bitstrings
                for b0, b1 in encodings[color]
            ]
        for bits in bitstrings:
            zeros = [q for q, bit in zip(problem_qubits, bits) if bit == 0]
            for q in zeros:
                qc.x(q)
            qc.mcp(3.141592653589793, controls, target)
            for q in reversed(zeros):
                qc.x(q)
```
