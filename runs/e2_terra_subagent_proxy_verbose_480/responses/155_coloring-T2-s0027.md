```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edge_flags = ancilla_qubits[:5]
    edges = ((0, 1), (0, 2), (0, 3), (2, 3), (2, 4))

    def toggle_different(u: int, v: int, target: int,
                         inverse: bool = False) -> None:
        q = (
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
        )

        operations = (
            (0,),
            (1,),
            (2,),
            (3,),
            (1, 2),
            (0, 3),
            (0, 1, 2),
            (0, 1, 3),
            (0, 2, 3),
            (1, 2, 3),
        )
        if inverse:
            operations = operations[::-1]

        for controls in operations:
            if len(controls) == 1:
                qc.cx(q[controls[0]], target)
            elif len(controls) == 2:
                qc.ccx(q[controls[0]], q[controls[1]], target)
            else:
                qc.mcx([q[i] for i in controls], target)

    for (u, v), flag in zip(edges, edge_flags):
        toggle_different(u, v, flag)

    qc.h(edge_flags[4])
    qc.mcx(edge_flags[:4], edge_flags[4])
    qc.h(edge_flags[4])

    for (u, v), flag in reversed(tuple(zip(edges, edge_flags))):
        toggle_different(u, v, flag, inverse=True)
```
