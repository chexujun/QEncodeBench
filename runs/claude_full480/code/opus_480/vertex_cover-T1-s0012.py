from qiskit import QuantumCircuit
from math import pi

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    v = problem_qubits
    edges = [(0, 1), (0, 3), (1, 2), (1, 3)]

    edge_anc = ancilla_qubits[0:4]   # one ancilla per edge (edge covered flag)
    cnt = ancilla_qubits[4:7]        # 3-bit popcount of x (values 0..4)
    all_edges = edge_anc[0]          # reuse edge_anc[0]? no, need separate; use a dedicated below

    # --- compute edge-covered flags: edge_anc[i] = v_a OR v_b = NOT(NOT a AND NOT b) ---
    def edge_or(a, b, tgt):
        qc.x(a); qc.x(b)
        qc.ccx(a, b, tgt)   # tgt ^= (NOT a')(NOT b') ... after x, a is NOT a
        qc.x(a); qc.x(b)
        qc.x(tgt)           # tgt = a OR b

    for i, (a, b) in enumerate(edges):
        edge_or(v[a], v[b], edge_anc[i])

    # --- compute popcount of the 4 problem bits into cnt (3-bit ripple) ---
    # cnt starts at 0. Add each bit.
    def add_bit(bit, c0, c1, c2):
        # increment 3-bit counter (c0 lsb) conditioned on bit
        # carry chain: use controlled increment
        qc.ccx(bit, c1, c2)
        qc.ccx(bit, c0, c1)
        qc.cx(bit, c0)

    for i in range(4):
        add_bit(v[i], cnt[0], cnt[1], cnt[2])

    # size <= 2 means cnt <= 2, i.e. NOT (cnt == 3 or cnt == 4).
    # cnt==4 -> binary 100 -> c2=1. cnt==3 -> 011 -> c0=1,c1=1.
    # size<=2 predicate S = NOT(c2) AND NOT(c0 AND c1)
    # We want phase -1 iff all_edges_covered AND size<=2.
    # all_edges covered = AND of edge_anc[0..3].

    # Build a flag qubit for size>2 into a spare... we've used 7 ancillas (4 edge +3 cnt).
    # Encode condition directly with multi-controlled Z on the phase.
    # size<=2 : c2==0 and not(c0==1 and c1==1).
    # Split into two disjoint accepted count-patterns among reachable counts (0..4):
    #   accepted counts: 0(000),1(001),2(010). Rejected:3(011),4(100).
    # Predicate reject = c2 OR (c0 AND c1). Accept = NOT reject.
    # Combine: mark iff edge0&edge1&edge2&edge3 & NOT c2 & NOT(c0&c1).

    # Prepare NOT c2 and NOT(c0&c1) via temporary x on c2 for control-on-zero,
    # and handle (c0&c1) using control-on-zero pattern with an mcp phase.
    # Use two multi-controlled phase (pi) gates that together realize accept.
    # accept = A AND B where A = e0 e1 e2 e3 NOT c2, B-part removing c0&c1.
    # Since among reachable states, exactly count in {0,1,2} pass the count test,
    # equivalently pass = NOT c2 AND NOT(c0 AND c1).
    # Apply phase = product over the accepted region. Implement as:
    #   phase(-1) on states with e0e1e2e3=1, c2=0, and (c0,c1) != (1,1).
    # (c0,c1)!=(1,1) with c2=0 among reachable = counts 0,1,2 exactly.

    controls = edge_anc[0:4]

    # term for count==0: c0=0,c1=0,c2=0
    qc.x(cnt[0]); qc.x(cnt[1]); qc.x(cnt[2])
    qc.mcp(pi, controls + [cnt[0], cnt[1]], cnt[2])
    qc.x(cnt[0]); qc.x(cnt[1]); qc.x(cnt[2])

    # term for count==1: exactly one of c0 set (001): c0=1,c1=0,c2=0
    qc.x(cnt[1]); qc.x(cnt[2])
    qc.mcp(pi, controls + [cnt[0], cnt[1]], cnt[2])
    qc.x(cnt[1]); qc.x(cnt[2])

    # term for count==2: c0=0,c1=1,c2=0
    qc.x(cnt[0]); qc.x(cnt[2])
    qc.mcp(pi, controls + [cnt[0], cnt[1]], cnt[2])
    qc.x(cnt[0]); qc.x(cnt[2])

    # --- uncompute popcount (reverse order) ---
    def add_bit_inv(bit, c0, c1, c2):
        qc.cx(bit, c0)
        qc.ccx(bit, c0, c1)
        qc.ccx(bit, c1, c2)

    for i in range(3, -1, -1):
        add_bit_inv(v[i], cnt[0], cnt[1], cnt[2])

    # --- uncompute edge flags (reverse order) ---
    def edge_or_inv(a, b, tgt):
        qc.x(tgt)
        qc.x(a); qc.x(b)
        qc.ccx(a, b, tgt)
        qc.x(a); qc.x(b)

    for i in range(3, -1, -1):
        a, b = edges[i]
        edge_or_inv(v[a], v[b], edge_anc[i])
