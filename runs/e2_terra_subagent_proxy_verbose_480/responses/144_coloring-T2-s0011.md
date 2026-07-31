```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # One ancilla per edge records whether that edge is monochromatic.
    # The final ancilla temporarily stores the parity of one endpoint code.
    edge_flags = ancilla_qubits[:5]
    work = ancilla_qubits[5]
    edges = ((0, 1), (0, 4), (1, 2), (2, 3), (3, 4))

    def controlled_x(controls, target, zero_controls=()):
        zero_controls = set(zero_controls)
        for qubit in zero_controls:
            qc.x(qubit)
        qc.mcx(controls, target)
        for qubit in reversed(controls):
            if qubit in zero_controls:
                qc.x(qubit)

    def compute_equal(v, w, target):
        vl, vh = problem_qubits[2 * v], problem_qubits[2 * v + 1]
        wl, wh = problem_qubits[2 * w], problem_qubits[2 * w + 1]

        # work = vl XOR vh.  It is 0 precisely for decoded color 0.
        qc.cx(vl, work)
        qc.cx(vh, work)

        # Both vertices decode to color 0: work=0 and wl==wh.
        controlled_x([work, wl, wh], target, (work, wl, wh))
        controlled_x([work, wl, wh], target, (work,))

        # Both decode to color 1 or both decode to color 2.
        # With work=1, matching decoded nonzero colors means
        # wl=vl and wh=not wl.
        controlled_x([work, vl, wl, wh], target, (vl, wl))
        controlled_x([work, vl, wl, wh], target, (wh,))

        qc.cx(vh, work)
        qc.cx(vl, work)

    for (v, w), flag in zip(edges, edge_flags):
        compute_equal(v, w, flag)

    # Convert "edge is monochromatic" flags to "edge is proper" flags,
    # then phase-flip exactly when all five edges are proper.
    for flag in edge_flags:
        qc.x(flag)
    qc.h(edge_flags[-1])
    qc.mcx(edge_flags[:-1], edge_flags[-1])
    qc.h(edge_flags[-1])
    for flag in reversed(edge_flags):
        qc.x(flag)

    for (v, w), flag in reversed(list(zip(edges, edge_flags))):
        compute_equal(v, w, flag)
```
