```python
def build_oracle():
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(13)
    qc.x(0)
    qc.x(2)
    qc.h(3)
    qc.mcx([0, 1, 2], 3)
    qc.h(3)
    qc.x(2)
    qc.x(0)
    return qc
```
