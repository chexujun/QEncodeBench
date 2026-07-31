```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[4])

    qc.h(problem_qubits[4])
    qc.mcx(problem_qubits[:4], problem_qubits[4],
           ancilla_qubits=ancilla_qubits, mode="v-chain")
    qc.h(problem_qubits[4])

    qc.x(problem_qubits[4])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[1])
```
