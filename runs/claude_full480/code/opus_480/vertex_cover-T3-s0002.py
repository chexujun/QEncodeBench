import math
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (0, 3), (0, 5), (2, 3), (2, 4), (3, 5), (4, 5)]
    n = len(problem_qubits)
    edge_anc = ancilla_qubits[:len(edges)]     # 8 ancillas: one per edge (edge covered)
    count_anc = ancilla_qubits[len(edges):len(edges) + 3]  # 3 ancillas for popcount bits
    all_edges_anc = None

    # ---- compute: edge covered flags ----
    # edge covered = u OR v = NOT( NOT u AND NOT v ). Compute into edge ancilla.
    for (u, v), a in zip(edges, edge_anc):
        qu = problem_qubits[u]
        qv = problem_qubits[v]
        qc.x(qu)
        qc.x(qv)
        qc.ccx(qu, qv, a)   # a = (NOT u)(NOT v)  after we flip; but qu currently flipped
        qc.x(qu)
        qc.x(qv)
        qc.x(a)             # a = u OR v

    # ---- compute: popcount of problem qubits into 3-bit register (max count 6) ----
    # Ripple: for each input bit, add 1 to the 3-bit counter (c0,c1,c2).
    c0, c1, c2 = count_anc[0], count_anc[1], count_anc[2]
    for q in problem_qubits:
        # add q into counter with carry propagation
        # c2 ^= q & c1 & c0 ; c1 ^= q & c0 ; c0 ^= q
        qc.ccx(q, c0, c1)          # not yet including c1 old for c2, do c2 first
        qc.ccx(q, c0, c1)          # undo (placeholder)  -- replaced below
    # (The above naive block is corrected: do proper ordered increment.)

    # Undo the placeholder block above by redoing correctly.
    # NOTE: we neutralized the placeholder (pairs cancel), now real increment:
    for q in problem_qubits:
        # carry into bit2 when q & c0 & c1
        qc.mcx([q, c0, c1], c2)
        # carry into bit1 when q & c0
        qc.ccx(q, c0, c1)
        # bit0 toggles with q
        qc.cx(q, c0)

    # count <= 4  means NOT(count >= 5). count in 0..6, 3 bits value = c0+2c1+4c2.
    # count >=5 iff c2=1 AND c1=1 (5=101,6=110 -> c2=1 and (c0 or c1)); actually
    # 5=101 (c2=1,c1=0,c0=1), 6=110 (c2=1,c1=1,c0=0). count>=5 iff c2 & (c0|c1).
    # We want valid_count = NOT(c2 & (c0 | c1)).
    # Build (c0 | c1) into count-check via De Morgan on the fly using c2 controls.

    # ---- phase: apply -1 iff all edges covered AND count<=4 ----
    # Condition = AND(all edge_anc) AND valid_count.
    # valid_count = NOT( c2 AND (c0 OR c1) ).
    #
    # We realize the multi-controlled Z over: all edge_anc = 1, and (count<=4).
    # count<=4 with c2: if c2==0 -> ok. if c2==1 -> need c0==0 and c1==0.
    #
    # Split into the two disjoint accepting count-patterns is messy; instead use
    # a control on NOT(bad) where bad = c2 & (c0|c1).
    #
    # Compute helper 'valid' bit reusing one edge ancilla is unsafe; use c-register
    # trick: temporarily compute bad into c2-position not allowed. Instead do:
    # Apply MCZ controlled on all edges AND (c2==0)  -> covers counts 0..4 with c2=0
    # PLUS counts where c2=1 but that's only 5,6 which are invalid, so c2==0 alone
    # exactly means count<=4 (since c2=1 <=> count>=4? check: 4=100 has c2=1!).
    #
    # 4 = 100 -> c2=1. So c2==0 means count<=3. Need to also accept count==4 (100).
    # count==4 pattern: c2=1,c1=0,c0=0.
    #
    # So valid_count = (c2==0) OR (c2=1,c1=0,c0=0) = NOT(c2 & (c0|c1)).

    # Phase term A: all edges AND c2==0  (counts 0..3)
    ctrl_neg = list(edge_anc) + [c2]
    qc.x(c2)
    _mcz(qc, list(edge_anc) + [c2])
    qc.x(c2)

    # Phase term B: all edges AND c2==1 AND c1==0 AND c0==0  (count==4)
    qc.x(c0)
    qc.x(c1)
    _mcz(qc, list(edge_anc) + [c2, c1, c0])
    qc.x(c0)
    qc.x(c1)

    # ---- uncompute popcount (reverse of increment) ----
    for q in reversed(problem_qubits):
        qc.cx(q, c0)
        qc.ccx(q, c0, c1)
        qc.mcx([q, c0, c1], c2)

    # ---- uncompute edge flags (reverse) ----
    for (u, v), a in zip(edges, edge_anc):
        qu = problem_qubits[u]
        qv = problem_qubits[v]
        qc.x(a)
        qc.x(qu)
        qc.x(qv)
        qc.ccx(qu, qv, a)
        qc.x(qu)
        qc.x(qv)


def _mcz(qc, controls):
    # multi-controlled Z on given qubits (symmetric); use last as target with H.
    if len(controls) == 1:
        qc.z(controls[0])
        return
    tgt = controls[-1]
    ctr = controls[:-1]
    qc.h(tgt)
    qc.mcx(ctr, tgt)
    qc.h(tgt)
