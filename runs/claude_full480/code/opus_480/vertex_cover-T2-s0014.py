import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    edge_anc = ancilla_qubits[0:4]        # covered-flag per edge
    c0, c1, c2 = ancilla_qubits[4:7]      # 3-bit little-endian popcount

    edges = [(0, 3), (1, 3), (2, 3), (2, 4)]

    # compute: edge covered = x_u OR x_v
    for a, (u, v) in zip(edge_anc, edges):
        qc.cx(x[u], a)
        qc.cx(x[v], a)
        qc.ccx(x[u], x[v], a)

    # compute: popcount of x into (c0,c1,c2) via controlled increment
    def cinc(ctrl):
        qc.mcx([ctrl, c0, c1], c2)   # carry into bit2
        qc.ccx(ctrl, c0, c1)         # carry into bit1
        qc.cx(ctrl, c0)              # bit0
    for xi in x:
        cinc(xi)

    # phase -1 on: all edges covered AND count in {0,1,2}
    # count<=2  <=>  c2==0 AND (c0,c1)!=(1,1); enumerate allowed (c0,c1)
    ctrls = list(edge_anc) + [c0, c1, c2]
    for b0, b1 in [(0, 0), (1, 0), (0, 1)]:
        flips = []
        if b0 == 0:
            qc.x(c0); flips.append(c0)
        if b1 == 0:
            qc.x(c1); flips.append(c1)
        qc.x(c2); flips.append(c2)   # require c2==0
        qc.mcp(math.pi, ctrls[:-1], ctrls[-1])
        for q in flips:
            qc.x(q)

    # uncompute popcount
    def cinc_inv(ctrl):
        qc.cx(ctrl, c0)
        qc.ccx(ctrl, c0, c1)
        qc.mcx([ctrl, c0, c1], c2)
    for xi in reversed(x):
        cinc_inv(xi)

    # uncompute edges
    for a, (u, v) in zip(reversed(edge_anc), reversed(edges)):
        qc.ccx(x[u], x[v], a)
        qc.cx(x[v], a)
        qc.cx(x[u], a)
