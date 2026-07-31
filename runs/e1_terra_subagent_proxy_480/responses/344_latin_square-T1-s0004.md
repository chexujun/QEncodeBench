```python
def build_oracle():
    qc = QuantumCircuit(13)
    for a in (0, 1):
        for b in (0, 1):
            bits = (a, a, b, b)
            for q, bit in enumerate(bits):
                if bit == 0:
                    qc.x(q)
            qc.h(3)
            qc.mcx([0, 1, 2], 3)
            qc.h(3)
            for q, bit in enumerate(bits):
                if bit == 0:
                    qc.x(q)
    return qc
```
