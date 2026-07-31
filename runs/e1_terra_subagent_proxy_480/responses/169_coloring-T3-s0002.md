```python
from qiskit import QuantumCircuit

def build_oracle():
    qc = QuantumCircuit(16)
    count0, count1, count2, flag = 12, 13, 14, 15
    edges = [(0, 2), (0, 5), (1, 2), (1, 3), (2, 3), (3, 4), (3, 5)]
    def toggle_equal(u, v):
        bits = [2*u,2*u+1,2*v,2*v+1]
        for pattern in ("0000","0011","1100","1111","0101","1010"):
            for bit,value in zip(bits,pattern):
                if value=="0": qc.x(bit)
            qc.mcx(bits, flag, ancilla_qubits=[count0,count1], mode="v-chain-dirty")
            for bit,value in reversed(list(zip(bits,pattern))):
                if value=="0": qc.x(bit)
    def increment():
        qc.mcx([flag,count0,count1],count2); qc.ccx(flag,count0,count1); qc.cx(flag,count0)
    def decrement():
        qc.cx(flag,count0); qc.ccx(flag,count0,count1); qc.mcx([flag,count0,count1],count2)
    for u,v in edges: toggle_equal(u,v); increment(); toggle_equal(u,v)
    qc.x(count0);qc.x(count1);qc.x(count2);qc.h(count2);qc.ccx(count0,count1,count2);qc.h(count2);qc.x(count2);qc.x(count1);qc.x(count0)
    for u,v in reversed(edges): toggle_equal(u,v); decrement(); toggle_equal(u,v)
    return qc
```
