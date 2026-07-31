from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits, ancilla_qubits) -> None:
    # Vertex cover, 6 vertices, edges; f=1 iff every edge covered AND popcount<=4.
    edges = [(0,3),(0,5),(1,2),(1,3),(1,4),(1,5),(3,5)]
    p = problem_qubits
    n = len(edges)

    # ancillas: n edge-ancillas (0..n-1), plus count/comparison ancillas.
    edge_anc = ancilla_qubits[:n]            # 7 edge ancillas
    rest = ancilla_qubits[n:]                # 3 remaining ancillas

    # --- compute edge coverage: edge_anc[j] = OR(x_u, x_v) = NOT(AND(NOT x_u, NOT x_v)) ---
    for j,(u,v) in enumerate(edges):
        qc.x(p[u]); qc.x(p[v])
        qc.ccx(p[u], p[v], edge_anc[j])   # edge_anc = AND(notu,notv) currently (with x applied)
        qc.x(p[u]); qc.x(p[v])
        qc.x(edge_anc[j])                 # now edge_anc = OR(u,v) = covered
    # all-edges-covered predicate = AND of all edge_anc.

    # --- popcount <= 4 over 6 problem bits: equivalently NOT(popcount>=5).
    # popcount>=5 over 6 bits means at least 5 ones, i.e. sum in {5,6}.
    # "cover_ok AND count_ok" where count_ok = (popcount <= 4).
    # We compute count_bad = (popcount>=5) into an ancilla, then predicate = cover_all AND (NOT count_bad).

    # Compute popcount using a small binary counter into 3 count qubits (values 0..6 need 3 bits).
    c0, c1, c2 = rest[0], rest[1], rest[2]  # count register bits (LSB c0)
    # add each problem bit into the 3-bit counter via controlled increments.
    for i in range(6):
        ctrl = p[i]
        # increment 3-bit counter controlled on ctrl: ripple carry
        # bit2 ^= ctrl & c1 & c0
        qc.mcx([ctrl, c1, c0], c2)
        # bit1 ^= ctrl & c0
        qc.ccx(ctrl, c0, c1)
        # bit0 ^= ctrl
        qc.cx(ctrl, c0)

    # Now (c2 c1 c0) = popcount in binary. popcount>=5 iff value in {5=101,6=110}.
    # i.e. c2==1 AND (c1 OR c0). count_ok = NOT that = NOT(c2 AND (c1 or c0)).
    # predicate = (AND all edge_anc) AND count_ok.

    # Build phase: apply -1 iff all edge_anc==1 AND NOT(c2 AND (c1 or c0)).
    # Handle count_ok via casework using multi-controlled Z with c2 negated OR c1,c0 both zero.
    # count_ok = (c2==0) OR (c1==0 AND c0==0).
    # We phase iff cover_all AND count_ok. Split into disjoint cases:
    #   Case A: c2==0  -> count_ok true.
    #   Case B: c2==1 AND c1==0 AND c0==0 (value 4? no, that's 100=4) -> count_ok true.
    # Note value 4 = 100 has c2=1,c1=0,c0=0 and popcount 4 <=4 ok. Values 5,6 excluded; 7 impossible.
    # So count_ok true sets: c2==0 (any c1,c0) OR (c2==1,c1==0,c0==0).

    cover = edge_anc  # all must be 1

    # Case A: multi-controlled Z on all cover ==1 and c2==0.
    qc.x(c2)
    qc.h(cover[-1])
    qc.mcx(cover[:-1] + [c2], cover[-1])
    qc.h(cover[-1])
    qc.x(c2)

    # Case B: cover all ==1 and c2==1 and c1==0 and c0==0.
    qc.x(c1); qc.x(c0)
    qc.h(cover[-1])
    qc.mcx(cover[:-1] + [c2, c1, c0], cover[-1])
    qc.h(cover[-1])
    qc.x(c1); qc.x(c0)

    # --- uncompute popcount counter (reverse of increments) ---
    for i in reversed(range(6)):
        ctrl = p[i]
        qc.cx(ctrl, c0)
        qc.ccx(ctrl, c0, c1)
        qc.mcx([ctrl, c1, c0], c2)

    # --- uncompute edge coverage ---
    for j,(u,v) in enumerate(edges):
        qc.x(edge_anc[j])
        qc.x(p[u]); qc.x(p[v])
        qc.ccx(p[u], p[v], edge_anc[j])
        qc.x(p[u]); qc.x(p[v])
