```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    from itertools import permutations, product
    q=list(problem_qubits); encodings={0:((0,0),(1,1)),1:((0,1),),2:((1,0),)}
    for c_a,c_b,c_c in permutations((0,1,2)):
        vertices=((0,c_a),(3,c_a),(5,c_a),(1,c_b),(2,c_b),(4,c_c)); choices=[encodings[color] for _,color in vertices]
        for bits_per_vertex in product(*choices):
            bits=[0]*12
            for (vertex,_),(hi,lo) in zip(vertices,bits_per_vertex): bits[2*vertex]=hi; bits[2*vertex+1]=lo
            flipped=[q[i] for i,bit in enumerate(bits) if bit==0]; qc.x(flipped); qc.mcp(3.141592653589793,q[:-1],q[-1]); qc.x(flipped)
```
