```python
def build_oracle(qc, problem_qubits, ancilla_qubits) -> None:
    def xor_poly(*polys):
        result = set()
        for poly in polys:
            for monomial in poly:
                if monomial in result:
                    result.remove(monomial)
                else:
                    result.add(monomial)
        return result

    def mul_poly(left, right):
        result = set()
        for a in left:
            for b in right:
                monomial = a | b
                if monomial in result:
                    result.remove(monomial)
                else:
                    result.add(monomial)
        return result

    colors = []
    for v in range(6):
        a = 1 << (2 * v)
        b = 1 << (2 * v + 1)
        colors.append((
            {0, a, b},       # decoded color 0: 00 or 11
            {b, a | b},      # decoded color 1: 01
            {a, a | b},      # decoded color 2: 10
        ))

    proper = {0}
    for u, v in ((0, 1), (0, 3), (0, 4), (1, 3), (1, 5), (2, 5), (4, 5)):
        equal = xor_poly(*(mul_poly(colors[u][c], colors[v][c]) for c in range(3)))
        valid = xor_poly({0}, equal)
        proper = mul_poly(proper, valid)

    phase = ancilla_qubits[0]
    qc.x(phase)
    qc.h(phase)
    for monomial in sorted(proper):
        if monomial:
            controls = [
                problem_qubits[i]
                for i in range(12)
                if monomial & (1 << i)
            ]
            qc.mcx(controls, phase)
    qc.h(phase)
    qc.x(phase)
```
