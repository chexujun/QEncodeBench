```python
def build_oracle(qc, q, ancillas):
    qc.x(q[0])
    qc.x(q[2])
    qc.h(q[3])
    qc.mcx([q[0], q[1], q[2]], q[3])
    qc.h(q[3])
    qc.x(q[2])
    qc.x(q[0])
```
