from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 1), (0, 3), (1, 2), (1, 3), (1, 4)]
    p = problem_qubits
    edge_anc = ancilla_qubits[0:5]      # one per edge: 1 iff edge covered
    cover_anc = ancilla_qubits[5]       # 1 iff all edges covered
    count_anc = ancilla_qubits[6:8]     # 2-bit popcount accumulator (max count that matters is 3)
    # We need popcount(x) <= 2 over 5 bits. Count with a 3-bit-ish accumulator,
    # but we only need to detect >=3. Use 2 carry-detect ancillas plus reuse.
    # Simpler robust approach: compute popcount into a small register using count_anc (2 bits)
    # and a spare. Only 2 ancillas remain (indices 6,7); we detect popcount<=2 via
    # a threshold circuit using those 2 qubits as a saturating counter capped at 3.

    # Saturating 2-bit counter (caps at 3 = 0b11). If final value <= 2 -> allowed by count.
    # count_anc[0] = low bit, count_anc[1] = high bit. Saturating increment for each xi.
    c0, c1 = count_anc[0], count_anc[1]

    def sat_inc(xi):
        # increment (c1 c0) by 1 if xi==1, saturating at 3.
        # new_c1 = c1 OR (xi AND c0);  new_c0 = c0 XOR (xi AND NOT c1)
        # order matters: compute c1 update using old c0, then c0 update using old c1.
        # c1 ^= xi & c0
        qc.ccx(xi, c0, c1)
        # c0 ^= xi & ~c1  ->  use c1 as control-0: apply x to c1, ccx, x to c1
        qc.x(c1)
        qc.ccx(xi, c1, c0)
        qc.x(c1)

    def sat_inc_inv(xi):
        # inverse of sat_inc (mirror)
        qc.x(c1)
        qc.ccx(xi, c1, c0)
        qc.x(c1)
        qc.ccx(xi, c0, c1)

    # ---- COMPUTE popcount (saturating) ----
    for i in range(5):
        sat_inc(p[i])

    # ---- COMPUTE edge coverage ----
    for j, (u, v) in enumerate(edges):
        a = edge_anc[j]
        # edge covered = u OR v  = NOT( NOT u AND NOT v )
        qc.x(p[u]); qc.x(p[v])
        qc.ccx(p[u], p[v], a)   # a = (~u_orig ... ) careful: after x, controls are 1 iff original 0
        qc.x(a)                 # a = 1 iff at least one endpoint in cover
        qc.x(p[u]); qc.x(p[v])

    # ---- all edges covered ----
    qc.mcx(edge_anc, cover_anc)

    # ---- PHASE: mark iff cover_anc==1 AND popcount<=2 (i.e. NOT(c1 AND c0)) ----
    # popcount<=2 means (c1,c0) != (1,1). Condition = cover_anc AND NOT(c1 AND c0).
    # Apply -1 phase controlled on cover_anc, and c1&c0 both 1 excluded.
    # Use: phase = cover_anc AND (NOT (c0 AND c1)).
    # Implement multi-controlled Z on cover_anc with control-0 on the "c0 AND c1" combined.
    # Build combined = c0 AND c1 into count reg? Instead do two mcp terms via inclusion-exclusion:
    # mark(cover AND everything) minus overlap. Cleaner: controlled-Z on {cover_anc} with
    # an extra control that is 0 exactly when NOT(c0&c1). Use a temporary AND of c0,c1 into edge_anc? all used.
    # Use relative-phase trick: Z on cover_anc gives -1 for all cover states; we must undo -1
    # for states where c0&c1 also 1. Net: mcp(pi, cover_anc) then mcp(-pi? ) ...
    # Do: apply Z-phase for (cover_anc==1); then apply +pi phase (undo) for (cover_anc==1 & c0==1 & c1==1).
    qc.mcp(math.pi, [], cover_anc) if False else qc.z(cover_anc)
    # undo phase where cover & c0 & c1:
    qc.mcp(math.pi, [cover_anc, c0], c1)  # applies pi phase when cover_anc=1,c0=1,c1=1 -> cancels the -1

    # ---- UNCOMPUTE (mirror everything) ----
    qc.mcx(edge_anc, cover_anc)

    for j in range(len(edges) - 1, -1, -1):
        u, v = edges[j]
        a = edge_anc[j]
        qc.x(p[u]); qc.x(p[v])
        qc.x(a)
        qc.ccx(p[u], p[v], a)
        qc.x(p[u]); qc.x(p[v])

    for i in range(4, -1, -1):
        sat_inc_inv(p[i])
