```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    from itertools import combinations
    from math import pi

    flags = ancilla_qubits[:5]

    for offset, flag in enumerate(flags):
        qc.mcx(problem_qubits[offset:offset + 4], flag)

    for size in range(1, 6):
        for subset in combinations(flags, size):
            if len(subset) == 1:
                qc.z(subset[0])
            else:
                qc.mcp(pi, list(subset[:-1]), subset[-1])

    for offset, flag in reversed(list(enumerate(flags))):
        qc.mcx(problem_qubits[offset:offset + 4], flag)
```
