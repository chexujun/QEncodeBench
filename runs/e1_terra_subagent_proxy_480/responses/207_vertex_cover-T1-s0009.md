```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit) -> None:
    qc.cx(2, 4)
    qc.cx(3, 4)

    qc.x(1)
    qc.h(4)
    qc.mcx([0, 1], 4)
    qc.h(4)
    qc.x(1)

    qc.cx(3, 4)
    qc.cx(2, 4)
```
