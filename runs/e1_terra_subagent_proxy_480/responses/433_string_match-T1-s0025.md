```python
from qiskit import QuantumCircuit

def build_oracle(problem_qubits, ancilla_qubits):
    qc = QuantumCircuit(problem_qubits + ancilla_qubits)
    qc.cz(1, 2)
    return qc
```
