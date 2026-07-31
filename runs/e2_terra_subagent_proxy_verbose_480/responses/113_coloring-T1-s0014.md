```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    flags = ancilla_qubits[:4]
    scratch = ancilla_qubits[4]

    def compute_not_equal(a, b, c, d, flag):
        # Equality of decoded colors, in algebraic normal form:
        # 1 + a+b+c+d + ad+bc + abc+abd+acd+bcd.
        # Start with 1 xor equality, i.e. the "not equal" flag.
        qc.x(flag)
        qc.cx(a, flag)
        qc.cx(b, flag)
        qc.cx(c, flag)
        qc.cx(d, flag)
        qc.ccx(a, d, flag)
        qc.ccx(b, c, flag)

        # abc xor abd
        qc.ccx(a, b, scratch)
        qc.ccx(scratch, c, flag)
        qc.ccx(scratch, d, flag)
        qc.ccx(a, b, scratch)

        # acd xor bcd
        qc.ccx(c, d, scratch)
        qc.ccx(scratch, a, flag)
        qc.ccx(scratch, b, flag)
        qc.ccx(c, d, scratch)

    edges = ((0, 3), (1, 4), (2, 3), (3, 4))

    for (u, v), flag in zip(edges, flags):
        compute_not_equal(
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
            flag,
        )

    qc.mcp(math.pi, flags[:3], flags[3])

    for (u, v), flag in reversed(list(zip(edges, flags))):
        compute_not_equal(
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
            flag,
        )
```
