```python
from itertools import product
from qiskit import QuantumCircuit
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    edges=((0,1),(0,3),(0,4),(1,2),(1,3),(1,4),(2,4))
    phase_qubit=ancilla_qubits[0]
    for bits in product((0,1),repeat=10):
        colors=[(lambda c: c if c<3 else 0)(bits[2*v]+2*bits[2*v+1]) for v in range(5)]
        if not all(colors[u]!=colors[v] for u,v in edges): continue
        zero_bits=[problem_qubits[i] for i,b in enumerate(bits) if b==0]
        qc.x(zero_bits); qc.h(phase_qubit); qc.mcx(problem_qubits,phase_qubit); qc.h(phase_qubit); qc.x(zero_bits)
```
