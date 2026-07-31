import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    v = problem_qubits  # v[i] == 1 means vertex i in cover
    edges = [(0, 2), (0, 3), (0, 4), (0, 5), (1, 3), (1, 5),
             (2, 3), (2, 5), (3, 4), (4, 5)]
    k = 3
    n = len(v)

    # Ancilla layout:
    #   edge_anc: 10 ancillas, one per edge (edge covered flag)
    #   we need to also compute popcount <= k.
    # Budget: 13 ancillas.
    #
    # Strategy:
    #   - For each edge (a,b): edge is covered iff v[a] OR v[b].
    #     Compute OR into an edge ancilla.
    #   - AND all 10 edge-covered flags together => "all edges covered".
    #   - Compute a count register (weight of x) and a flag "count <= 3".
    #   - Final predicate = all_edges_covered AND count_leq_k.
    #
    # We reuse ancillas via compute/uncompute nesting.

    edge_anc = ancilla_qubits[0:10]   # 10 edge flags
    # remaining 3 ancillas for counting/aggregation
    cnt = ancilla_qubits[10:13]       # 3-qubit counter (0..6 needs 3 bits)

    # ---- compute edge-covered flags ----
    # OR(a,b) = NOT(AND(NOT a, NOT b)) -> put into fresh ancilla=0:
    #   anc = a OR b computed as: x a; x b; anc = a&b (ccx) gives NOT a & NOT b;
    #   then x anc -> a OR b; then restore a,b.
    def or_into(a, b, t):
        qc.x(v[a]); qc.x(v[b])
        qc.ccx(v[a], v[b], t)   # t = (¬a)&(¬b)
        qc.x(v[a]); qc.x(v[b])
        qc.x(t)                 # t = a OR b

    def or_into_inv(a, b, t):
        qc.x(t)
        qc.x(v[a]); qc.x(v[b])
        qc.ccx(v[a], v[b], t)
        qc.x(v[a]); qc.x(v[b])

    for (a, b), t in zip(edges, edge_anc):
        or_into(a, b, t)

    # ---- compute count register cnt = popcount(v) using increments ----
    # 3-bit ripple counter. For each vertex qubit, add 1 controlled on v[i].
    # Increment of a 3-bit register controlled by ctrl:
    #   bit2 ^= ctrl & bit1 & bit0
    #   bit1 ^= ctrl & bit0
    #   bit0 ^= ctrl
    c0, c1, c2 = cnt[0], cnt[1], cnt[2]

    def inc(ctrl):
        qc.mcx([ctrl, c0, c1], c2)
        qc.ccx(ctrl, c0, c1)
        qc.cx(ctrl, c0)

    def inc_inv(ctrl):
        qc.cx(ctrl, c0)
        qc.ccx(ctrl, c0, c1)
        qc.mcx([ctrl, c0, c1], c2)

    for i in range(n):
        inc(v[i])

    # count <= 3 means the value is in {0,1,2,3}, i.e. bit2 == 0
    # (since max count = 6, values 4,5,6 have bit2==1; value<=3 <=> c2==0).
    # So predicate_count = NOT c2.

    # ---- phase: -1 iff (all edge flags == 1) AND (c2 == 0) ----
    # controls: all 10 edge_anc == 1, and c2 == 0.
    qc.x(c2)  # now c2==1 means count<=3
    ctrl_list = list(edge_anc) + [c2]
    qc.h(edge_anc[0])
    qc.mcx(ctrl_list[1:], edge_anc[0])
    qc.h(edge_anc[0])
    qc.x(c2)

    # ---- uncompute count ----
    for i in reversed(range(n)):
        inc_inv(v[i])

    # ---- uncompute edge flags ----
    for (a, b), t in zip(reversed(edges), reversed(edge_anc)):
        or_into_inv(a, b, t)
