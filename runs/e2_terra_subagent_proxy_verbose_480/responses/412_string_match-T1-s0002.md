```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Match 000010: x0=x1=x2=x3=x5=0 and x4=1.
    zero_bits = [problem_qubits[i] for i in (0, 1, 2, 3, 5)]
    target = problem_qubits[4]

    for qubit in zero_bits:
        qc.x(qubit)

    qc.h(target)
    qc.mcx(zero_bits, target)
    qc.h(target)

    for qubit in reversed(zero_bits):
        qc.x(qubit)
```
