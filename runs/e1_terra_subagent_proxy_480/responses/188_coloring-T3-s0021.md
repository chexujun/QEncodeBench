```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    from itertools import permutations
    for v in range(6):
        qc.cx(problem_qubits[2 * v + 1], problem_qubits[2 * v])
    for c0, c2, c5 in permutations((0, 1, 2)):
        for c1 in (c for c in (0, 1, 2) if c != c5):
            colors = (c0, c1, c2, c5, c0, c5); literals=[]; zero_literals=[]
            for v, color in enumerate(colors):
                x=problem_qubits[2*v]; y=problem_qubits[2*v+1]
                if color==0: literals.append(x); zero_literals.append(x)
                elif color==1: literals.extend((x,y)); zero_literals.append(y)
                else: literals.extend((x,y))
            for q in zero_literals: qc.x(q)
            target=literals[-1]; qc.h(target); qc.mcx(literals[:-1],target,ancilla_qubits=ancilla_qubits[:1],mode="recursion"); qc.h(target)
            for q in reversed(zero_literals): qc.x(q)
    for v in reversed(range(6)): qc.cx(problem_qubits[2*v+1],problem_qubits[2*v])
```
