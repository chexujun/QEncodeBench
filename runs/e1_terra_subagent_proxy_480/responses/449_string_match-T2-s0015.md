```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    x=problem_qubits; t0,t1,t2=ancilla_qubits[:3]
    qc.ccx(x[1],x[2],t0); qc.ccx(x[2],x[3],t1); qc.ccx(x[3],x[4],t2)
    qc.z(t0); qc.z(t1); qc.z(t2); qc.cz(t0,t1); qc.cz(t0,t2); qc.cz(t1,t2); qc.h(t2); qc.ccx(t0,t1,t2); qc.h(t2)
    qc.ccx(x[3],x[4],t2); qc.ccx(x[2],x[3],t1); qc.ccx(x[1],x[2],t0)
```
