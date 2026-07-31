import math
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    v = problem_qubits
    edges = [(0, 2), (1, 3), (1, 4), (2, 3), (3, 4)]

    edge_anc = ancilla_qubits[0:5]     # one ancilla per edge (OR of endpoints)
    cnt = ancilla_qubits[5:8]          # 3-bit popcount register (counts 1-bits, 0..5)
    pred = None                        # we reuse an edge ancilla region carefully

    # ---------- COMPUTE popcount of the 5 problem bits into cnt (3 bits) ----------
    # cnt starts at |000>. Add each vertex bit via a ripple increment.
    def add_bit(ctrl):
        # cnt += ctrl  (3-bit, max value 5 so no overflow past 3 bits used as 0..7)
        # carry chain: bit2 ^= ctrl & cnt0 & cnt1 ; bit1 ^= ctrl & cnt0 ; bit0 ^= ctrl
        qc.mcx([ctrl, cnt[0], cnt[1]], cnt[2])
        qc.ccx(ctrl, cnt[0], cnt[1])
        qc.cx(ctrl, cnt[0])

    def unadd_bit(ctrl):
        qc.cx(ctrl, cnt[0])
        qc.ccx(ctrl, cnt[0], cnt[1])
        qc.mcx([ctrl, cnt[0], cnt[1]], cnt[2])

    for i in range(5):
        add_bit(v[i])

    # ---------- COMPUTE edge OR ancillas ----------
    # edge_anc[e] = 1 iff edge e is covered (endpoint a OR endpoint b)
    for e, (a, b) in enumerate(edges):
        qc.x(v[a]); qc.x(v[b])
        qc.ccx(v[a], v[b], edge_anc[e])
        qc.x(edge_anc[e])
        qc.x(v[a]); qc.x(v[b])

    # ---------- PHASE ----------
    # f = (all edges covered) AND (popcount <= 3)
    # popcount <= 3 over value 0..5 in 3-bit cnt (cnt2 cnt1 cnt0, value = cnt0 + 2cnt1 + 4cnt2):
    #   values 4 and 5 are the only ones > 3 (4=100,5=101). Both have cnt2=1 and cnt1=0.
    #   So popcount<=3  <=>  NOT (cnt2==1 AND cnt1==0).
    # Predicate true controls: all 5 edge_anc == 1, cnt2 handled below.
    # Apply -1 phase iff (all edges) AND NOT(cnt2 & ~cnt1).
    #
    # Use decomposition: phase(all edges covered) minus phase(all edges & cnt2 & ~cnt1).
    # Instead directly: mark = edges_all AND (cnt2==0 OR cnt1==1).
    #
    # Realize with two multi-controlled-Z terms via inclusion is messy; instead build
    # the "size>3" flag then AND with edges and subtract. Simpler: compute a single
    # predicate ancilla.
    pflag = cnt  # placeholder; we need one more ancilla but all 8 used.
    # All 8 ancillas used (5 edge + 3 cnt). We phase without extra ancilla using mcp.

    # Condition A: all edges covered  -> controls edge_anc all =1
    # Condition B: popcount<=3        -> NOT(cnt2=1 & cnt1=0)
    # Split B: either cnt2=0, or (cnt2=1 & cnt1=1).
    # phase(-1) over A AND B = phase over [A & cnt2=0] + phase over [A & cnt2=1 & cnt1=1]
    # These two regions are disjoint, so applying an MCZ on each gives the correct
    # combined -1 on exactly A&B.

    # Region 1: A and cnt2 == 0
    qc.x(cnt[2])
    ctrls1 = list(edge_anc) + [cnt[2]]
    qc.h(cnt[2]) if False else None
    # multi-controlled Z: use mcp(pi)
    qc.mcp(math.pi, ctrls1[:-1], ctrls1[-1])
    qc.x(cnt[2])

    # Region 2: A and cnt2 == 1 and cnt1 == 1
    ctrls2 = list(edge_anc) + [cnt[2], cnt[1]]
    qc.mcp(math.pi, ctrls2[:-1], ctrls2[-1])

    # ---------- UNCOMPUTE edge OR ancillas ----------
    for e, (a, b) in reversed(list(enumerate(edges))):
        qc.x(v[a]); qc.x(v[b])
        qc.x(edge_anc[e])
        qc.ccx(v[a], v[b], edge_anc[e])
        qc.x(v[a]); qc.x(v[b])

    # ---------- UNCOMPUTE popcount ----------
    for i in reversed(range(5)):
        unadd_bit(v[i])
