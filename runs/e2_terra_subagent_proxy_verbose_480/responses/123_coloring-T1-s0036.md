```python
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    def compute_equal(v1: int, v2: int, target: int) -> None:
        l1, h1 = problem_qubits[2 * v1], problem_qubits[2 * v1 + 1]
        l2, h2 = problem_qubits[2 * v2], problem_qubits[2 * v2 + 1]

        # Transform high bits to d = low XOR high.  d=0 denotes color 0.
        qc.cx(l1, h1)
        qc.cx(l2, h2)
        qc.cx(l1, l2)

        # Both decoded colors are 0: d1=d2=0.
        qc.x(h1)
        qc.x(h2)
        qc.ccx(h1, h2, target)
        qc.x(h2)
        qc.x(h1)

        # Both are nonzero and identical: d1=d2=1 and original low bits match.
        qc.x(l2)
        qc.mcx([h1, h2, l2], target)
        qc.x(l2)

        qc.cx(l1, l2)
        qc.cx(l2, h2)
        qc.cx(l1, h1)

    edge_ancillas = ancilla_qubits[:3]
    phase_ancilla = ancilla_qubits[3]
    edges = [(0, 1), (0, 2), (2, 3)]

    # Store edge-satisfaction bits: 1 iff the decoded endpoint colors differ.
    for (u, v), ancilla in zip(edges, edge_ancillas):
        compute_equal(u, v, ancilla)
        qc.x(ancilla)

    qc.mcx(edge_ancillas, phase_ancilla)
    qc.z(phase_ancilla)
    qc.mcx(edge_ancillas, phase_ancilla)

    # Uncompute all predicate workspace.
    for (u, v), ancilla in reversed(list(zip(edges, edge_ancillas))):
        qc.x(ancilla)
        compute_equal(u, v, ancilla)
```
