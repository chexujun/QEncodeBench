```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    for i in (0, 2, 4): qc.x(problem_qubits[i])
    qc.h(problem_qubits[4]); qc.mcx(list(problem_qubits[:4]),problem_qubits[4],ancilla_qubits=list(ancilla_qubits),mode="v-chain"); qc.h(problem_qubits[4])
    for i in (0, 2, 4): qc.x(problem_qubits[i])
```
