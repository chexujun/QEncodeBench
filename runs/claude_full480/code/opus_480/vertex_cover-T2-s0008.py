import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    edges = [(0, 1), (0, 3), (1, 2), (1, 3), (2, 3), (2, 4)]

    # Ancilla layout:
    # edge_anc[j] for j in 0..5  -> one ancilla per edge (a_j = OR of endpoints)
    # count ancillas: we need to test popcount(x) <= 3, i.e. NOT(popcount >= 4).
    # We use 3 ancillas to build a "popcount >= 4" flag via a small adder-free
    # threshold network, then combine with the edge flags into the final MCX.
    #
    # We have 9 ancillas total. Use 6 for edges, and 3 for the count threshold.
    edge_anc = ancilla_qubits[0:6]
    cnt = ancilla_qubits[6:9]   # binary counter bits c0,c1,c2 (value 0..5, cap at needing bit2 for >=4)

    def compute():
        # --- edge OR flags: a_j = v_a OR v_b = NOT( (NOT v_a) AND (NOT v_b) ) ---
        for j, (u, v) in enumerate(edges):
            a = edge_anc[j]
            qc.x(x[u]); qc.x(x[v])
            qc.ccx(x[u], x[v], a)      # a = (NOT? ) -> here a = v_u AND v_v after we flipped -> a = (¬vu ∧ ¬vv)
            qc.x(x[u]); qc.x(x[v])
            qc.x(a)                    # a = ¬(¬vu ∧ ¬vv) = vu OR vv

        # --- popcount into 3-bit counter cnt = [c0,c1,c2] over the 5 vertices ---
        # ripple increment: for each vertex bit, add 1 to the counter controlled on x[i].
        for i in range(5):
            ctrl = x[i]
            # add 1: carry chain c0 -> c1 -> c2
            # increment: c2 ^= ctrl & c0 & c1 ; c1 ^= ctrl & c0 ; c0 ^= ctrl
            qc.mcx([ctrl, cnt[0], cnt[1]], cnt[2])
            qc.ccx(ctrl, cnt[0], cnt[1])
            qc.cx(ctrl, cnt[0])

    def uncompute():
        # reverse of compute
        for i in reversed(range(5)):
            ctrl = x[i]
            qc.cx(ctrl, cnt[0])
            qc.ccx(ctrl, cnt[0], cnt[1])
            qc.mcx([ctrl, cnt[0], cnt[1]], cnt[2])
        for j, (u, v) in enumerate(edges):
            a = edge_anc[j]
            qc.x(a)
            qc.x(x[u]); qc.x(x[v])
            qc.ccx(x[u], x[v], a)
            qc.x(x[u]); qc.x(x[v])

    compute()

    # popcount <= 3  <=>  value in {0,1,2,3}  <=>  NOT(value >= 4).
    # value >= 4 means (c2 == 1) OR (value >= 4 with c2 set). For counts 0..5,
    # value >= 4  <=>  c2 == 1 AND (c1==1 or c0==1)?  Let's check binary:
    #   4 = 100, 5 = 101.  So value>=4 <=> c2==1.  (max count 5 = 101, c2 bit = 1)
    # Thus popcount<=3 <=> c2 == 0.
    #
    # Phase -1 iff (all 6 edge flags == 1) AND (c2 == 0).
    # Control on c2 == 0: flip c2 so control-on-1 works, then flip back.
    qc.x(cnt[2])
    controls = edge_anc + [cnt[2]]
    target = ancilla_qubits[6]  # reuse cnt[0]? no—need a clean target. Use phase via mcp.
    # Use a multi-controlled Z (phase) directly: mcp(pi) with last control as target.
    qc.h(controls[-1])
    qc.mcx(controls[:-1], controls[-1])
    qc.h(controls[-1])
    qc.x(cnt[2])

    uncompute()
