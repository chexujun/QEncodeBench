```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    def toggle_same_color(lu, hu, lv, hv, target):
        # ANF for equality of the decoded three-color values:
        # 1 + lu + hu + lv + hu*lv + lu*hu*lv + hv + lu*hv
        #   + lu*hu*hv + lu*lv*hv + hu*lv*hv
        qc.x(target)
        qc.cx(lu, target)
        qc.cx(hu, target)
        qc.cx(lv, target)
        qc.ccx(hu, lv, target)
        qc.mcx([lu, hu, lv], target)
        qc.cx(hv, target)
        qc.ccx(lu, hv, target)
        qc.mcx([lu, hu, hv], target)
        qc.mcx([lu, lv, hv], target)
        qc.mcx([hu, lv, hv], target)

    edge_flags = ancilla_qubits[:4]
    all_valid = ancilla_qubits[4]
    edges = ((0, 3), (1, 3), (2, 4), (3, 4))

    for (u, v), flag in zip(edges, edge_flags):
        toggle_same_color(
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
            flag,
        )

    qc.mcx(edge_flags, all_valid, ctrl_state=0)
    qc.z(all_valid)
    qc.mcx(edge_flags, all_valid, ctrl_state=0)

    for (u, v), flag in reversed(list(zip(edges, edge_flags))):
        toggle_same_color(
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
            flag,
        )
```
