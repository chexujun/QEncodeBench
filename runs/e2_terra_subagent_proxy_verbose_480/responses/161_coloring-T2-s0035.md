```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    edge_flags = ancilla_qubits[:7]
    success = ancilla_qubits[7]

    edges = [(0, 1), (0, 4), (1, 2), (1, 3), (1, 4), (2, 4), (3, 4)]

    def toggle_if_code_pair(target, v1, code1, v2, code2):
        q0 = problem_qubits[2 * v1]
        q1 = problem_qubits[2 * v1 + 1]
        q2 = problem_qubits[2 * v2]
        q3 = problem_qubits[2 * v2 + 1]
        controls = [q0, q1, q2, q3]
        values = [code1 & 1, (code1 >> 1) & 1,
                  code2 & 1, (code2 >> 1) & 1]

        for qubit, value in zip(controls, values):
            if value == 0:
                qc.x(qubit)

        qc.ccx(q2, q3, success)
        qc.mcx([q0, q1, success], target)
        qc.ccx(q2, q3, success)

        for qubit, value in reversed(list(zip(controls, values))):
            if value == 0:
                qc.x(qubit)

    def compute_edge_equal(target, u, v):
        # Decoded color 0 has codes 00 and 11.
        for cu in (0, 3):
            for cv in (0, 3):
                toggle_if_code_pair(target, u, cu, v, cv)

        # Colors 1 and 2 each have one code.
        toggle_if_code_pair(target, u, 1, v, 1)
        toggle_if_code_pair(target, u, 2, v, 2)

    for flag, (u, v) in zip(edge_flags, edges):
        compute_edge_equal(flag, u, v)

    # A valid coloring has no monochromatic edge.
    for flag in edge_flags:
        qc.x(flag)
    qc.mcx(edge_flags, success)
    qc.z(success)
    qc.mcx(edge_flags, success)
    for flag in reversed(edge_flags):
        qc.x(flag)

    for flag, (u, v) in reversed(list(zip(edge_flags, edges))):
        compute_edge_equal(flag, u, v)
```
