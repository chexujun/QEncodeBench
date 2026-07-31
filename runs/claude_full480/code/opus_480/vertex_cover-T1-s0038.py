from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q = problem_qubits
    edges = [(0, 1), (1, 2), (1, 3), (2, 3)]

    edge_anc = ancilla_qubits[0:4]   # one ancilla per edge (covered flag)
    cnt = ancilla_qubits[4:7]        # 3-qubit counter for popcount (0..4)
    # We need a "size <= 2" flag. Reuse edge_anc[0] AFTER edges freed? No—keep separate.
    # Total ancillas: 4 edges + 3 counter = 7. Phase computed via multi-controlled.

    # ---- compute: edge covered flags ----
    # edge covered iff (x_u OR x_v). covered flag a: set a=1 if covered.
    # a = x_u OR x_v = NOT( (NOT x_u) AND (NOT x_v) )
    for idx, (u, v) in enumerate(edges):
        a = edge_anc[idx]
        qc.x(q[u]); qc.x(q[v])
        qc.ccx(q[u], q[v], a)   # a = (NOT x_u)AND(NOT x_v) with the surrounding X's => a=1 iff both zero
        qc.x(q[u]); qc.x(q[v])
        qc.x(a)                 # a = covered (1 iff at least one endpoint in S)

    # ---- compute: popcount of the 4 problem qubits into 3-qubit counter cnt ----
    # counter add each x_i. cnt bits: cnt[0]=LSB, cnt[1], cnt[2]=MSB (value up to 4).
    def add_one(control):
        # increment counter conditioned on control
        # carry chain: c2 ^= control & c0 & c1 ; c1 ^= control & c0 ; c0 ^= control
        qc.mcx([control, cnt[0], cnt[1]], cnt[2])
        qc.ccx(control, cnt[0], cnt[1])
        qc.cx(control, cnt[0])

    for i in range(4):
        add_one(q[i])

    # size <= 2 means counter value in {0,1,2}, i.e. NOT (cnt >= 3).
    # cnt>=3 : values 3 (011) or 4 (100). value bits (cnt2 cnt1 cnt0):
    #   3 -> 0 1 1 ; 4 -> 1 0 0.
    # size_ok = NOT( (cnt2) OR (cnt1 AND cnt0) )
    # Build predicate P = AND(all edge_anc covered) AND size_ok, phase -1 when P.

    # Represent "cnt>=3" onto a fresh flag? No free ancilla. Instead fold into phase
    # via controlled logic using edge_anc as controls plus size condition directly.
    # size_ok controls: we phase iff all edges covered AND NOT(cnt2) AND NOT(cnt1&cnt0).
    #
    # Split into the two "bad size" complementary form: phase all-edges-covered states,
    # but only those with size<=2. Enumerate size>=3 as two multi-controlled subtract.
    #
    # Approach: apply an mcp(pi) (multi-controlled Z) with controls =
    #   all edge_anc (must be 1) AND size_ok expressed via control states.
    # size_ok = NOT cnt2 AND NOT(cnt1 AND cnt0).
    # Decompose: phase = [all edges] AND [NOT cnt2] AND [NOT(cnt1 AND cnt0)].
    # Use inclusion: Z_full over controls {edges..., cnt2=0, and handle cnt1&cnt0}.
    #
    # Implement as: total = (edges covered & cnt2=0) ; within that subtract states cnt1=cnt0=1.
    # Z(A) - but phases multiply; do: apply mcz over [edges, ~cnt2] then apply mcz over
    # [edges, ~cnt2, cnt1, cnt0] to CANCEL the cnt1&cnt0 (value 3) case.

    ctrl_edges = list(edge_anc)

    # Phase (pi) all states with edges covered and cnt2 == 0:
    qc.x(cnt[2])
    qc.mcp(math.pi, ctrl_edges + [cnt[2]], q[0]) if False else \
        qc.h(q[0])  # placeholder guard, replaced below
    qc.h(q[0])
    # (the two h() cancel; real phase applied next line)
    qc.mcp(math.pi, ctrl_edges + [cnt[2]] + [cnt[0]], cnt[1]) if False else None

    # Proper multi-controlled Z on (edges + ~cnt2): use last qubit as target of mcp.
    _c1 = ctrl_edges + [cnt[2]]
    qc.mcp(math.pi, _c1[:-1], _c1[-1])
    # Cancel the value==3 case (cnt2=0,cnt1=1,cnt0=1): apply same phase again on that subset
    _c2 = ctrl_edges + [cnt[2], cnt[1], cnt[0]]
    qc.mcp(math.pi, _c2[:-1], _c2[-1])
    qc.x(cnt[2])

    # ---- uncompute popcount (reverse order) ----
    def add_one_inv(control):
        qc.cx(control, cnt[0])
        qc.ccx(control, cnt[0], cnt[1])
        qc.mcx([control, cnt[0], cnt[1]], cnt[2])

    for i in reversed(range(4)):
        add_one_inv(q[i])

    # ---- uncompute edge flags ----
    for idx, (u, v) in reversed(list(enumerate(edges))):
        a = edge_anc[idx]
        qc.x(a)
        qc.x(q[u]); qc.x(q[v])
        qc.ccx(q[u], q[v], a)
        qc.x(q[u]); qc.x(q[v])
