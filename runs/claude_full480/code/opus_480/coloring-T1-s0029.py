from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (1, 3), (2, 3)]

    def vq(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    flag = [ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]]
    sc = ancilla_qubits[3]

    def is_color(bit0, bit1, k, target):
        # target ^= [vertex has color k]; self-inverse
        if k == 0:                       # color 0: code 00 or 11  <=> bit0==bit1
            qc.cx(bit0, target); qc.cx(bit1, target); qc.x(target)
        elif k == 1:                     # color 1: code 01 (bit0=1,bit1=0)
            qc.x(bit1); qc.ccx(bit0, bit1, target); qc.x(bit1)
        else:                            # color 2: code 10 (bit0=0,bit1=1)
            qc.x(bit0); qc.ccx(bit0, bit1, target); qc.x(bit0)

    def edge_block(u, v, cbit):
        # cbit ^= same_color(u,v); sc used as scratch and restored.
        u0, u1 = vq(u)
        v0, v1 = vq(v)
        for k in range(3):
            is_color(u0, u1, k, sc)              # sc = [u has color k]
            if k == 0:
                qc.x(v0); qc.x(v1)
                qc.mcx([sc, v0, v1], cbit)       # sc & code_v==00
                qc.x(v0); qc.x(v1)
                qc.mcx([sc, v0, v1], cbit)       # sc & code_v==11
            elif k == 1:
                qc.x(v1)
                qc.mcx([sc, v0, v1], cbit)       # sc & code_v==01
                qc.x(v1)
            else:
                qc.x(v0)
                qc.mcx([sc, v0, v1], cbit)       # sc & code_v==10
                qc.x(v0)
            is_color(u0, u1, k, sc)              # uncompute sc
        # exactly one color k per vertex => the contributions are disjoint,
        # so cbit becomes the OR, i.e. same_color(u,v).

    # compute conflict flag per edge
    for i, (u, v) in enumerate(edges):
        edge_block(u, v, flag[i])

    # f(x)=1 iff every edge differently colored, i.e. all flags == 0.
    qc.x(flag[0]); qc.x(flag[1]); qc.x(flag[2])
    qc.h(flag[2])
    qc.ccx(flag[0], flag[1], flag[2])
    qc.h(flag[2])
    qc.x(flag[0]); qc.x(flag[1]); qc.x(flag[2])

    # uncompute conflict flags (edge_block is its own inverse)
    for i, (u, v) in reversed(list(enumerate(edges))):
        edge_block(u, v, flag[i])
