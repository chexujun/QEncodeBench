from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (0, 4), (1, 3), (1, 4), (2, 3), (3, 4)]

    def qb(v, bit):
        return problem_qubits[2 * v + bit]

    # (a0,a1,b0,b1) code-bit patterns where the two endpoints share a color.
    # color(00)=color(11)=0, color(01)=1, color(10)=2.
    equal_patterns = [
        (0, 0, 0, 0), (0, 0, 1, 1), (1, 1, 0, 0), (1, 1, 1, 1),
        (1, 0, 1, 0), (0, 1, 0, 1),
    ]

    e = ancilla_qubits[0]                 # per-edge monochromatic flag
    c0, c1, c2 = ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]

    def set_equal(u, v):
        a0, a1, b0, b1 = qb(u, 0), qb(u, 1), qb(v, 0), qb(v, 1)
        ctrls = [a0, a1, b0, b1]
        for (p0, p1, q0, q1) in equal_patterns:
            qc.mcx(ctrls, e, ctrl_state=f"{q1}{q0}{p1}{p0}")

    def inc():
        qc.mcx([e, c0, c1], c2)
        qc.mcx([e, c0], c1)
        qc.cx(e, c0)

    def dec():
        qc.cx(e, c0)
        qc.mcx([e, c0], c1)
        qc.mcx([e, c0, c1], c2)

    for (u, v) in edges:
        set_equal(u, v)
        inc()
        set_equal(u, v)

    qc.x(c0); qc.x(c1); qc.x(c2)
    qc.h(c2)
    qc.mcx([c0, c1], c2)
    qc.h(c2)
    qc.x(c2); qc.x(c1); qc.x(c0)

    for (u, v) in reversed(edges):
        set_equal(u, v)
        dec()
        set_equal(u, v)
