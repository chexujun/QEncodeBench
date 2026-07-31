```python
def build_oracle(qc,problem_qubits,ancilla_qubits):
 for i in (1,2,3): qc.x(problem_qubits[i])
 qc.mcp(3.141592653589793,problem_qubits[:-1],problem_qubits[-1])
 for i in (3,2,1): qc.x(problem_qubits[i])
```
