```python
def build_oracle():
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(13)

    # Free cells: (1,1) uses q0,q1; (2,2) uses q2,q3.
    # Valid encodings are 00 or 11 for each cell (both decode to 0).
    qc.cx(0, 1)
    qc.cx(2, 3)
    qc.x(1)
    qc.x(3)
    qc.cz(1, 3)
    qc.x(3)
    qc.x(1)
    qc.cx(2, 3)
    qc.cx(0, 1)

    return qc
```
