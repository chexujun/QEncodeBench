```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[3])
    qc.h(problem_qubits[3])
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2]], problem_qubits[3])
    qc.h(problem_qubits[3])
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[0])

    qc.x(problem_qubits[0])
    qc.x(problem_qubits[2])
    qc.h(problem_qubits[3])
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2]], problem_qubits[3])
    qc.h(problem_qubits[3])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[0])
```
