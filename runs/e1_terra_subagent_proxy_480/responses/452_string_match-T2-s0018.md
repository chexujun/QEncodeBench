```python
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    for text in ("11010", "11011", "01101", "11101"):
        for qubit, bit in zip(problem_qubits, text):
            if bit == "0":
                qc.x(qubit)

        target = problem_qubits[-1]
        qc.h(target)
        qc.mcp(math.pi, problem_qubits[:-1], target)
        qc.h(target)

        for qubit, bit in zip(problem_qubits, text):
            if bit == "0":
                qc.x(qubit)
```
