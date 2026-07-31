```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    for a_zero in (True, False):
        for c_zero in (True, False):
            flips = [problem_qubits[4], problem_qubits[7]]
            if a_zero:
                flips += [problem_qubits[0], problem_qubits[1]]
            if c_zero:
                flips += [problem_qubits[2], problem_qubits[3]]
            for qubit in flips:
                qc.x(qubit)
            qc.h(problem_qubits[7])
            qc.mcx(problem_qubits[:7], problem_qubits[7])
            qc.h(problem_qubits[7])
            for qubit in reversed(flips):
                qc.x(qubit)
```
