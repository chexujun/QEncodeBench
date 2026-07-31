```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q = problem_qubits

    # Phase for s1=s2=s3=s4=1.
    qc.h(q[4])
    qc.mcx([q[1], q[2], q[3]], q[4])
    qc.h(q[4])

    # Phase for s2=s3=s4=s5=1.
    qc.h(q[5])
    qc.mcx([q[2], q[3], q[4]], q[5])
    qc.h(q[5])

    # Correct the double-counted overlap s1=s2=s3=s4=s5=1.
    qc.h(q[5])
    qc.mcx([q[1], q[2], q[3], q[4]], q[5])
    qc.h(q[5])
```
