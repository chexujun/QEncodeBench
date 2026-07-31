```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # a[0:3] hold whether each edge is monochromatic; a[3] is a phase target.
    edge_flags = ancilla_qubits[:3]
    phase_target = ancilla_qubits[3]

    def toggle_with_pattern(target, controls, values):
        for qubit, value in zip(controls, values):
            if value == 0:
                qc.x(qubit)
        if len(controls) == 2:
            qc.ccx(controls[0], controls[1], target)
        else:
            qc.mcx(controls, target)
        for qubit, value in reversed(list(zip(controls, values))):
            if value == 0:
                qc.x(qubit)

    # Change each high bit to low XOR high.  In this representation:
    #   color 0 -> high=0; color 1 -> (high, low)=(1, 1);
    #   color 2 -> (high, low)=(1, 0).
    for v in range(5):
        qc.cx(problem_qubits[2 * v], problem_qubits[2 * v + 1])

    def compute_monochromatic(u, v, target):
        ul, uh = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        vl, vh = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        # The three color-equality cases are mutually exclusive, so XOR is OR.
        toggle_with_pattern(target, [uh, vh], [0, 0])          # color 0
        toggle_with_pattern(target, [uh, ul, vh, vl], [1, 1, 1, 1])  # color 1
        toggle_with_pattern(target, [uh, ul, vh, vl], [1, 0, 1, 0])  # color 2

    edges = [(0, 3), (1, 2), (3, 4)]
    for (u, v), flag in zip(edges, edge_flags):
        compute_monochromatic(u, v, flag)

    # Mark precisely when no edge is monochromatic.
    for flag in edge_flags:
        qc.x(flag)
    qc.x(phase_target)
    qc.mcp(math.pi, edge_flags, phase_target)
    qc.x(phase_target)
    for flag in reversed(edge_flags):
        qc.x(flag)

    # Uncompute edge flags, then restore the problem-register encoding.
    for (u, v), flag in reversed(list(zip(edges, edge_flags))):
        compute_monochromatic(u, v, flag)

    for v in reversed(range(5)):
        qc.cx(problem_qubits[2 * v], problem_qubits[2 * v + 1])
```
