```python
def build_oracle(circuit, problem_qubits, ancilla_qubits):
    for i in range(3):
        circuit.x(problem_qubits[i]);circuit.x(problem_qubits[i+4]);circuit.h(problem_qubits[i+4])
        circuit.mcx([problem_qubits[i],problem_qubits[i+1],problem_qubits[i+2],problem_qubits[i+3]],problem_qubits[i+4])
        circuit.h(problem_qubits[i+4]);circuit.x(problem_qubits[i+4]);circuit.x(problem_qubits[i])
```
