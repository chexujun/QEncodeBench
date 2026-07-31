```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    # The graph's constraints are equivalently:
    # c0 = c3 != c4, c1 = c2 != c4, and c0 != c1.
    a0, a1, a2, a3, a4 = ancilla_qubits[:5]

    # Codes representing an equal decoded color:
    # color 0: 00 or 11; color 1: 01; color 2: 10.
    equal_code_pairs = (
        (0, 0), (0, 3), (3, 0), (3, 3), (1, 1), (2, 2)
    )

    def toggle_on_code_pair(vertex_a, vertex_b, target):
        controls = [
            problem_qubits[2 * vertex_a],
            problem_qubits[2 * vertex_a + 1],
            problem_qubits[2 * vertex_b],
            problem_qubits[2 * vertex_b + 1],
        ]
        for code_a, code_b in equal_code_pairs:
            bits = (
                code_a & 1,
                (code_a >> 1) & 1,
                code_b & 1,
                (code_b >> 1) & 1,
            )
            for qubit, bit in zip(controls, bits):
                if bit == 0:
                    qc.x(qubit)
            qc.mcx(controls, target)
            for qubit, bit in reversed(list(zip(controls, bits))):
                if bit == 0:
                    qc.x(qubit)

    # Compute the five simplified constraints.
    toggle_on_code_pair(0, 3, a0)  # c0 == c3
    toggle_on_code_pair(1, 2, a1)  # c1 == c2

    qc.x(a2)                       # c0 != c4
    toggle_on_code_pair(0, 4, a2)

    qc.x(a3)                       # c1 != c4
    toggle_on_code_pair(1, 4, a3)

    qc.x(a4)                       # c0 != c1
    toggle_on_code_pair(0, 1, a4)

    # Apply -1 exactly when all five constraint flags are true.
    qc.h(a4)
    qc.mcx([a0, a1, a2, a3], a4)
    qc.h(a4)

    # Uncompute all ancillas.
    toggle_on_code_pair(0, 1, a4)
    qc.x(a4)

    toggle_on_code_pair(1, 4, a3)
    qc.x(a3)

    toggle_on_code_pair(0, 4, a2)
    qc.x(a2)

    toggle_on_code_pair(1, 2, a1)
    toggle_on_code_pair(0, 3, a0)
```
