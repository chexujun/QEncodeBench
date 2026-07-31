```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    marked = ("0100", "0111")
    for bitstring in marked:
        for qubit, bit in zip(problem_qubits, bitstring):
            if bit == "0":
                qc.x(qubit)
        qc.mcp(3.141592653589793, problem_qubits[:-1], problem_qubits[-1])
        for qubit, bit in zip(problem_qubits, bitstring):
            if bit == "0":
                qc.x(qubit)
```
