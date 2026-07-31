```python
def build_oracle():
    from qiskit import QuantumCircuit

    oracle = QuantumCircuit(4)
    oracle.x([1, 2, 3])
    oracle.mcp(__import__("math").pi, [0, 1, 2, 3])
    oracle.x([1, 2, 3])
    return oracle
```
