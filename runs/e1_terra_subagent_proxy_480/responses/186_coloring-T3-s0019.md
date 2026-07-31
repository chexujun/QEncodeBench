```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    edges = ((0, 1), (0, 2), (0, 4), (1, 3),
             (1, 4), (2, 3), (2, 4), (3, 4))
    color = (0, 1, 2, 0)
    target = ancilla_qubits[0]
    work = [ancilla_qubits[1]]

    qc.x(target)
    qc.h(target)

    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    for e in range(4):
                        codes = (a, b, c, d, e)
                        if all(color[codes[u]] != color[codes[v]] for u, v in edges):
                            bits = []
                            for code in codes:
                                bits.extend((code & 1, (code >> 1) & 1))
                            zeros = [problem_qubits[i] for i, bit in enumerate(bits) if bit == 0]
                            qc.x(zeros)
                            qc.mcx(problem_qubits, target, ancilla_qubits=work, mode="recursion")
                            qc.x(zeros)

    qc.h(target)
    qc.x(target)
```
