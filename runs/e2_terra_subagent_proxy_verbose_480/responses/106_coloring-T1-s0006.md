```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # a[0:3] hold the three edge-equality flags; a[3] is temporary workspace.
    a0, a1, a2, work = ancilla_qubits

    def mcx_with_zero_controls(controls, zero_controls, target):
        for q in zero_controls:
            qc.x(q)
        qc.mcx(controls, target)
        for q in reversed(zero_controls):
            qc.x(q)

    def compute_equal(u, v, flag):
        ul, uh = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        vl, vh = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        # Both vertices decode to color 0 iff each has equal code bits.
        qc.x(work)
        qc.cx(ul, work)
        qc.cx(uh, work)
        mcx_with_zero_controls([work, vl, vh], [vl, vh], flag)
        qc.mcx([work, vl, vh], flag)
        qc.cx(uh, work)
        qc.cx(ul, work)
        qc.x(work)

        # The remaining equality cases are 01/01 and 10/10.
        mcx_with_zero_controls([ul, uh, vl, vh], [uh, vh], flag)
        mcx_with_zero_controls([ul, uh, vl, vh], [ul, vl], flag)

    edges = ((0, 2, a0), (1, 2, a1), (2, 3, a2))
    for u, v, flag in edges:
        compute_equal(u, v, flag)

    # Mark iff none of the three edges is monochromatic.
    for flag in (a0, a1, a2):
        qc.x(flag)
    qc.mcx([a0, a1, a2], work)
    qc.z(work)
    qc.mcx([a0, a1, a2], work)
    for flag in (a2, a1, a0):
        qc.x(flag)

    # Equality computations are self-inverse XORs into their flags.
    for u, v, flag in reversed(edges):
        compute_equal(u, v, flag)
```
