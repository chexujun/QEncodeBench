```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    def minterm_xor(controls, bits, target):
        controls = list(controls)
        for qubit, bit in zip(controls, bits):
            if bit == 0:
                qc.x(qubit)
        qc.mcx(controls, target)
        for qubit, bit in reversed(list(zip(controls, bits))):
            if bit == 0:
                qc.x(qubit)

    def compute_same_color(vertex_a, vertex_b, target):
        a0 = problem_qubits[2 * vertex_a]
        a1 = problem_qubits[2 * vertex_a + 1]
        b0 = problem_qubits[2 * vertex_b]
        b1 = problem_qubits[2 * vertex_b + 1]

        # Both decode to color 0 iff both codes have equal bits.
        # (1+a0+a1)(1+b0+b1), represented as an XOR polynomial.
        qc.x(target)
        for qubit in (a0, a1, b0, b1):
            qc.cx(qubit, target)
        for left, right in ((a0, b0), (a0, b1), (a1, b0), (a1, b1)):
            qc.ccx(left, right, target)

        # The remaining two equal-color cases: 01/01 and 10/10.
        minterm_xor((a0, a1, b0, b1), (1, 0, 1, 0), target)
        minterm_xor((a0, a1, b0, b1), (0, 1, 0, 1), target)

    edge_01, edge_02, edge_03 = ancilla_qubits[:3]

    compute_same_color(0, 1, edge_01)
    compute_same_color(0, 2, edge_02)
    compute_same_color(0, 3, edge_03)

    # Mark exactly when no edge is monochromatic.
    for qubit in (edge_01, edge_02, edge_03):
        qc.x(qubit)
    qc.mcp(math.pi, [edge_01, edge_02], edge_03)
    for qubit in (edge_03, edge_02, edge_01):
        qc.x(qubit)

    compute_same_color(0, 3, edge_03)
    compute_same_color(0, 2, edge_02)
    compute_same_color(0, 1, edge_01)
```
