```python
from itertools import product
from qiskit import QuantumCircuit
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    edges=((0,1),(0,2),(0,3),(1,2),(1,4),(2,3),(3,4))
    def color(bits,v): return bits[2*v]+2*bits[2*v+1] if bits[2*v:2*v+2]!=(1,1) else 0
    target=problem_qubits[-1]; controls=problem_qubits[:-1]
    for bits in product((0,1),repeat=10):
        if all(color(bits,u)!=color(bits,v) for u,v in edges):
            zero=[problem_qubits[i] for i,b in enumerate(bits) if b==0]
            qc.x(zero); qc.h(target); qc.mcx(controls,target,ancilla_qubits=ancilla_qubits[:1],mode='recursion'); qc.h(target); qc.x(zero)
```
