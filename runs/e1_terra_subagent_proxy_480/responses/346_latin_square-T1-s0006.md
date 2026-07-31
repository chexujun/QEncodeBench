```python
def build_oracle():
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(13)
    qc.x([0, 2, 12])
    qc.h(12)
    qc.mcx([0, 1, 2, 3], 12)
    qc.h(12)
    qc.x([0, 2, 12])
    return qc
```
