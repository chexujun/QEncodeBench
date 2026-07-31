```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (0, 3), (0, 4), (1, 4), (3, 4)]
    edge_flags = ancilla_qubits[:5]
    phase_flag = ancilla_qubits[5]
    def edge_operations(u, v, target):
        a, b, c, d = problem_qubits[2*u], problem_qubits[2*u+1], problem_qubits[2*v], problem_qubits[2*v+1]
        return [("x", (), target), ("cx", (a,), target), ("cx", (b,), target), ("cx", (d,), target), ("ccx", (a,c), target), ("ccx", (a,d), target), ("ccx", (c,d), target), ("ccx", (b,c), target), ("mcx", (a,b,c), target), ("mcx", (a,b,d), target), ("mcx", (b,c,d), target)]
    def apply(ops):
        for gate, controls, target in ops:
            if gate == "x": qc.x(target)
            elif gate == "cx": qc.cx(controls[0], target)
            elif gate == "ccx": qc.ccx(controls[0], controls[1], target)
            else: qc.mcx(list(controls), target)
    edge_circuits=[]
    for (u,v), target in zip(edges, edge_flags):
        ops=edge_operations(u,v,target); edge_circuits.append(ops); apply(ops)
    for flag in edge_flags: qc.x(flag)
    qc.mcx(edge_flags, phase_flag); qc.z(phase_flag); qc.mcx(edge_flags, phase_flag)
    for flag in reversed(edge_flags): qc.x(flag)
    for ops in reversed(edge_circuits): apply(reversed(ops))
```
