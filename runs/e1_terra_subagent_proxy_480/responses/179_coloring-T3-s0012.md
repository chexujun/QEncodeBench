```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    codes=((0,0),(1,0),(0,1));solutions=((1,1,0,1,2),(2,2,0,2,1),(0,0,1,0,2),(2,2,1,2,0),(0,0,2,0,1),(1,1,2,1,0))
    target=problem_qubits[-1];controls=list(problem_qubits[:-1])
    for coloring in solutions:
        bits=[]
        for color in coloring: bits.extend(codes[color])
        zero_bits=[problem_qubits[index] for index,bit in enumerate(bits) if bit==0]
        qc.x(zero_bits);qc.h(target);qc.mcx(controls,target,ancilla_qubits=list(ancilla_qubits),mode="recursion");qc.h(target);qc.x(zero_bits)
```
