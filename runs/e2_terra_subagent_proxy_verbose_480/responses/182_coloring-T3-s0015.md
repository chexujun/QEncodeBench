```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0, a1, a2, a3 = ancilla_qubits

    def bits_of_code(code):
        return (code & 1, (code >> 1) & 1)

    # Toggle target iff the two encoded vertices decode to the same color.
    def equal_toggle(v, w, target):
        q = [problem_qubits[2 * v], problem_qubits[2 * v + 1],
             problem_qubits[2 * w], problem_qubits[2 * w + 1]]
        equal_code_pairs = ((0, 0), (0, 3), (3, 0),
                            (3, 3), (1, 1), (2, 2))
        for left, right in equal_code_pairs:
            pattern = bits_of_code(left) + bits_of_code(right)
            open_controls = [qubit for qubit, bit in zip(q, pattern)
                             if bit == 0]
            for qubit in open_controls:
                qc.x(qubit)
            qc.mcx(q, target)
            for qubit in reversed(open_controls):
                qc.x(qubit)

    # Toggle target iff the decoded colors differ.
    def different_toggle(v, w, target):
        qc.x(target)
        equal_toggle(v, w, target)

    # a2 = D(1,0) AND D(1,2) AND D(1,3).
    different_toggle(1, 0, a1)
    different_toggle(1, 2, a3)
    qc.ccx(a1, a3, a0)
    different_toggle(1, 2, a3)
    different_toggle(1, 0, a1)

    different_toggle(1, 3, a1)
    qc.ccx(a0, a1, a2)
    different_toggle(1, 3, a1)

    # Clear temporary a0 while preserving a2.
    different_toggle(1, 0, a1)
    different_toggle(1, 2, a3)
    qc.ccx(a1, a3, a0)
    different_toggle(1, 2, a3)
    different_toggle(1, 0, a1)

    # a0 = D(1,4) AND E(0,2).
    different_toggle(1, 4, a1)
    equal_toggle(0, 2, a3)
    qc.ccx(a1, a3, a0)
    equal_toggle(0, 2, a3)
    different_toggle(1, 4, a1)

    # The remaining constraints are E(3,4) and D(0,4).
    equal_toggle(3, 4, a1)
    different_toggle(0, 4, a3)
    qc.mcp(math.pi, [a0, a1, a2], a3)
    different_toggle(0, 4, a3)
    equal_toggle(3, 4, a1)

    # Uncompute a0.
    different_toggle(1, 4, a1)
    equal_toggle(0, 2, a3)
    qc.ccx(a1, a3, a0)
    equal_toggle(0, 2, a3)
    different_toggle(1, 4, a1)

    # Uncompute a2.
    different_toggle(1, 0, a1)
    different_toggle(1, 2, a3)
    qc.ccx(a1, a3, a0)
    different_toggle(1, 2, a3)
    different_toggle(1, 0, a1)

    different_toggle(1, 3, a1)
    qc.ccx(a0, a1, a2)
    different_toggle(1, 3, a1)

    different_toggle(1, 0, a1)
    different_toggle(1, 2, a3)
    qc.ccx(a1, a3, a0)
    different_toggle(1, 2, a3)
    different_toggle(1, 0, a1)
```
