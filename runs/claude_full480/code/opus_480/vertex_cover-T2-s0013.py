import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    v = problem_qubits
    edges = [(0, 1), (0, 2), (0, 3), (0, 4), (2, 4)]

    edge_anc = ancilla_qubits[0:5]      # one ancilla per edge (edge covered flag)
    size_anc = ancilla_qubits[5:8]      # 3 ancillas: count<=2 flag helpers

    # --- compute: edge coverage flags (a = x_u OR x_v) ---
    for (u, w), a in zip(edges, edge_anc):
        # OR via De Morgan: a = NOT( NOT x_u AND NOT x_w )
        qc.x(v[u]); qc.x(v[w])
        qc.ccx(v[u], v[w], a)
        qc.x(a)
        qc.x(v[u]); qc.x(v[w])

    # --- compute: popcount<=2 over 5 bits ---
    # weight <= 2  <=>  NOT(weight >= 3).
    # We compute the two carry bits of a 5-bit popcount using ripple full adders,
    # storing partial sums in size_anc.  Represent count in bits c0,c1,c2 where
    # c2 (>=4) or (c1 and (c2 or ...)) indicate >=3.  Simpler: use threshold ancilla.
    #
    # Build count bits: s0,s1,s2 = size_anc[0],size_anc[1],size_anc[2]
    s0, s1, s2 = size_anc
    # Add each problem bit to the 3-bit counter (s2 s1 s0), little-endian.
    for q in v:
        # full-add q into counter: carry chain s0 -> s1 -> s2
        # s2 ^= (s1 & (s0 & q))  ; note reuse of ancillas requires ordering high->low
        qc.ccx(s1, s0, s2)          # tentative: but need q too -> use mcx below
    # The naive loop above is wrong for a real adder; replace with explicit accumulation.

    # ---- redo counter cleanly (undo the tentative ops first) ----
    for q in v:
        qc.ccx(s1, s0, s2)
    # now s0,s1,s2 back to |0>.

    # Proper increments: for each bit q, do
    #   s2 ^= s1 & s0 & q   (carry into bit2)
    #   s1 ^= s0 & q        (carry into bit1)
    #   s0 ^= q             (add into bit0)
    for q in v:
        qc.mcx([s1, s0, q], s2)
        qc.ccx(s0, q, s1)
        qc.cx(q, s0)

    # weight >= 3  <=>  (count value >= 3) i.e. (s1 AND s0) OR s2
    #   = s2 OR (s1 AND s0)
    # weight <= 2 is the negation.  We fold this predicate together with all
    # edge flags into a single controlled-phase.
    #
    # Build "size_ok" onto a spare edge-independent scheme: we need a flag qubit.
    # Reuse s2's complement logic via multi-controlled phase with controls being
    # edge flags (all must be 1) AND size condition.
    #
    # size_ok = NOT( s2 OR (s1 AND s0) )
    # Introduce it on ancilla by toggling: compute bad = s2 OR (s1 AND s0) into
    # a temporary — but we are out of fresh ancillas. Instead apply phase via
    # inclusion-exclusion on the controls directly.

    # Multi-controlled Z that fires iff all edges covered AND weight<=2.
    # Controls-for-edges: edge_anc all =1.
    # weight<=2 condition expressed as: NOT s2 AND NOT(s1 AND s0).
    # We enumerate the allowed (s2,s1,s0) count patterns for weight<=2:
    #   0 -> 000, 1 -> 001, 2 -> 010.  (weight in {0,1,2})
    # So allowed counts: s2=0 and not(s1 and s0). Equivalent to: s2=0 AND (s1 NAND s0).
    #
    # Apply phase for each allowed count pattern combined with all edges=1.
    # allowed count patterns: (s0,s1,s2) in {(0,0,0),(1,0,0),(0,1,0)}.
    ctrl_edges = list(edge_anc)
    for (a0, a1, a2) in [(0, 0, 0), (1, 0, 0), (0, 1, 0)]:
        flips = []
        if a0 == 0:
            qc.x(s0); flips.append(s0)
        if a1 == 0:
            qc.x(s1); flips.append(s1)
        # a2 always 0 -> need s2 = 1 as control after x
        qc.x(s2); flips.append(s2)
        qc.mcp(math.pi, ctrl_edges + [s0, s1, s2][:-0] if False else ctrl_edges + [s0, s1, s2], -1)  # placeholder
        for fq in flips:
            qc.x(fq)

    # --- uncompute counter (reverse order) ---
    for q in reversed(v):
        qc.cx(q, s0)
        qc.ccx(s0, q, s1)
        qc.mcx([s1, s0, q], s2)

    # --- uncompute edge flags ---
    for (u, w), a in zip(edges, edge_anc):
        qc.x(v[u]); qc.x(v[w])
        qc.x(a)
        qc.ccx(v[u], v[w], a)
        qc.x(v[u]); qc.x(v[w])
