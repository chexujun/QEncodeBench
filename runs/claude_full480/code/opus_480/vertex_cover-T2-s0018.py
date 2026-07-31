import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Vertex cover instance
    edges = [(0, 3), (0, 4), (1, 3), (1, 4), (2, 4), (3, 4)]
    n = 5
    k = 3

    p = problem_qubits
    # Ancilla layout:
    #   edge_anc[j] : one ancilla per edge (6), = 1 iff edge j is covered
    #   We will reuse edge ancillas after ANDing.
    # We have 9 ancillas total.
    edge_anc = ancilla_qubits[0:6]      # 6 ancillas for edge-covered flags
    cnt = ancilla_qubits[6:9]           # 3 ancillas for popcount (bits 0..2 -> counts 0..7)
    # Final predicate flag lives on one of the edge ancillas after edges are AND-ed;
    # but we need a clean qubit. We'll use edge_anc[0] as the AND accumulator target
    # by an alternative: compute all-edges-covered into a single flag using MCX over
    # the edge ancillas, storing into cnt-region requires a free qubit. Instead we
    # allocate the AND result onto one edge ancilla by a 6-controlled X into cnt is
    # not possible (cnt used for popcount). So do phase via a big MCX gate directly.

    # ---- compute edge-covered flags: edge_anc[j] = p[u] OR p[v] ----
    def edge_compute():
        for j, (u, v) in enumerate(edges):
            a = edge_anc[j]
            # OR(x,y) = 1 - (1-x)(1-y): a = x OR y
            qc.x(p[u]); qc.x(p[v])
            qc.x(a)
            qc.ccx(p[u], p[v], a)
            qc.x(p[u]); qc.x(p[v])

    def edge_uncompute():
        for j, (u, v) in enumerate(edges):
            a = edge_anc[j]
            qc.x(p[u]); qc.x(p[v])
            qc.ccx(p[u], p[v], a)
            qc.x(a)
            qc.x(p[u]); qc.x(p[v])

    # ---- popcount of p into 3-bit register cnt (little-endian) ----
    # Add each problem qubit into the 3-bit counter using ripple increment
    # controlled by p[i]. Counter starts at |000>.
    def inc_controlled(ctrl):
        # increment 3-bit counter cnt (cnt[0] lsb) controlled by ctrl
        # add 1: carry chain. Use control on each step.
        # cnt2 ^= ctrl & cnt1 & cnt0 ; cnt1 ^= ctrl & cnt0 ; cnt0 ^= ctrl
        qc.mcx([ctrl, cnt[0], cnt[1]], cnt[2])
        qc.ccx(ctrl, cnt[0], cnt[1])
        qc.cx(ctrl, cnt[0])

    def dec_controlled(ctrl):
        qc.cx(ctrl, cnt[0])
        qc.ccx(ctrl, cnt[0], cnt[1])
        qc.mcx([ctrl, cnt[0], cnt[1]], cnt[2])

    def count_compute():
        for i in range(n):
            inc_controlled(p[i])

    def count_uncompute():
        for i in range(n - 1, -1, -1):
            dec_controlled(p[i])

    # popcount <= 3  <=>  count in {0,1,2,3}  <=>  bit cnt[2] == 0
    # (since max count = 5, values 4,5 have cnt[2]=1). Actually 3-bit:
    #   0..3 -> cnt[2]=0 ; 4,5 -> cnt[2]=1. So predicate size<=3 == NOT cnt[2].

    edge_compute()
    count_compute()

    # Phase -1 iff (all 6 edge flags == 1) AND (cnt[2] == 0).
    # Controls: edge_anc[0..5] must be 1, cnt[2] must be 0 -> X it to control on 1.
    qc.x(cnt[2])
    controls = list(edge_anc) + [cnt[2]]
    # apply Z on last control via H-MCX-H -> multi-controlled Z (phase flip when all controls=1)
    target = controls[-1]
    ctrl_rest = controls[:-1]
    qc.h(target)
    qc.mcx(ctrl_rest, target)
    qc.h(target)
    qc.x(cnt[2])

    count_uncompute()
    edge_uncompute()
