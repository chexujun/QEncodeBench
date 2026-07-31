```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    # For an edge u--v, compute into target whether decoded colors differ.
    # ANF: a+b+c+d+abc+abd+bc+acd+ad+bcd,
    # where a,b are u's low/high bits and c,d are v's.
    def edge_good(u, v, target):
        a = problem_qubits[2 * u]
        b = problem_qubits[2 * u + 1]
        c = problem_qubits[2 * v]
        d = problem_qubits[2 * v + 1]

        qc.cx(a, target)
        qc.cx(b, target)
        qc.cx(c, target)
        qc.cx(d, target)
        qc.mcx([a, b, c], target)
        qc.mcx([a, b, d], target)
        qc.ccx(b, c, target)
        qc.mcx([a, c, d], target)
        qc.ccx(a, d, target)
        qc.mcx([b, c, d], target)

    edges = [
        (0, 4), (0, 5), (1, 3), (1, 4),
        (2, 3), (2, 5), (3, 4), (3, 5),
    ]
    flags = ancilla_qubits[:4]
    aggregate = ancilla_qubits[4]

    for edge, flag in zip(edges[:4], flags):
        edge_good(*edge, flag)

    qc.mcx(flags, aggregate)

    for edge, flag in zip(edges[4:], flags):
        edge_good(*edge, flag)

    qc.h(flags[0])
    qc.mcx([aggregate, flags[1], flags[2], flags[3]], flags[0])
    qc.h(flags[0])

    for edge, flag in reversed(list(zip(edges[4:], flags))):
        edge_good(*edge, flag)

    qc.mcx(flags, aggregate)

    for edge, flag in reversed(list(zip(edges[:4], flags))):
        edge_good(*edge, flag)
```
