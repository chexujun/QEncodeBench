```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    phase=ancilla_qubits[0]; q=problem_qubits
    colorings=[(0,1,2,0,2),(0,2,1,0,1),(1,0,2,1,2),(1,2,0,1,0),(2,0,1,2,1),(2,1,0,2,0)]
    qc.x(phase); qc.h(phase)
    for coloring in colorings:
        for zero_code in ((0,0),(1,1)):
            bits=[]
            for color in coloring: bits.extend(zero_code if color==0 else ((0,1) if color==1 else (1,0)))
            for qubit,bit in zip(q,bits):
                if bit==0: qc.x(qubit)
            qc.mcx(q,phase)
            for qubit,bit in zip(q,bits):
                if bit==0: qc.x(qubit)
    qc.h(phase); qc.x(phase)
```
