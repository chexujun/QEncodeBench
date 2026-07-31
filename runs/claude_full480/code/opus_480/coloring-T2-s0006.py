from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 3), (0, 4), (1, 2), (1, 3), (2, 3), (2, 4)]

    def qb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    edge_anc = ancilla_qubits[:len(edges)]      # 7 ancillas, one per edge "same color?"
    final = ancilla_qubits[len(edges)]          # 1 ancilla for AND of "all different"

    # For each edge, compute e = 1 iff the two vertices have the SAME color.
    # Colors: c=0 ->(00), c=1 ->(01), c=2 ->(10), c=3 ->(00 color 0).
    # Same color pairs (u_code, v_code) where decode(u)==decode(v):
    #   color0 codes {00,11}, color1 code {01}, color2 code {10}.
    # decode maps: 00->0, 11->0, 01->1, 10->2.
    # Same color iff (both in {00,11}) or (both 01) or (both 10).
    def color_indicator_terms(v, target):
        # returns list of (b0_val, b1_val) codes decoding to `target`
        codes = {0: [(0, 0), (1, 1)], 1: [(1, 0)], 2: [(0, 1)]}
        return codes[target]

    def apply_code_flags(v, code, anc, undo=False):
        # flip anc controlled on vertex v == code (b0,b1)
        b0, b1 = qb(v)
        b0v, b1v = code
        pre = []
        if b0v == 0:
            qc.x(b0); pre.append(b0)
        if b1v == 0:
            qc.x(b1); pre.append(b1)
        qc.ccx(b0, b1, anc)
        for q in pre:
            qc.x(q)

    def compute_edge_same(u, v, out, tmp0, tmp1):
        # tmp0 = 1 iff u and v both decode to color depending... build per color
        # We compute out = OR over colors t of (u==color t AND v==color t)
        for t in (0, 1, 2):
            ucodes = color_indicator_terms(u, t)
            vcodes = color_indicator_terms(v, t)
            # tmp0 = (u decodes to t): OR over its codes
            for c in ucodes:
                apply_code_flags(u, c, tmp0)
            for c in vcodes:
                apply_code_flags(v, c, tmp1)
            # out ^= tmp0 AND tmp1
            qc.ccx(tmp0, tmp1, out)
            # uncompute tmp1, tmp0
            for c in reversed(vcodes):
                apply_code_flags(v, c, tmp1)
            for c in reversed(ucodes):
                apply_code_flags(u, c, tmp0)

    tmpA = ancilla_qubits[len(edges) + 0] if len(ancilla_qubits) > len(edges) + 1 else None

    # We only have 8 ancillas: 7 edge + 1 final. Reuse edge ancillas' scratch is tricky.
    # Instead compute each edge_same sequentially using two shared scratch qubits,
    # but we lack them. So reallocate: use 6 edge-result + 2 scratch? Need 7 edge results.
    # Simpler: compute edge_same[i] into edge_anc[i] using scratch = final and one more.
    # We reserve 2 scratch qubits and store 6 edge results, then handle last edge inline.
    # To stay safe, redefine layout below.

    # ---- Robust layout ----
    scratch0 = ancilla_qubits[6]
    scratch1 = ancilla_qubits[7]
    edge_res = ancilla_qubits[0:6]  # only 6 storage; we need 7. Combine last two edges.

    # Compute "same color" flags. We want f=1 iff NO edge is monochromatic,
    # i.e. all edge_same == 0. Phase -1 on that. Equivalent: phase -1 iff
    # AND over edges of (NOT edge_same). Use multi-controlled Z on the negations.

    # Compute each edge_same into a storage qubit; for 7 edges with 6 storage,
    # process edges 0..5 into edge_res, and edge 6 into scratch-based storage
    # right before the phase using an extra reuse of scratch1 as its store while
    # scratch0 acts as the two-qubit scratch (only need one scratch at the end).

    # Compute edges 0..5
    for i in range(6):
        u, v = edges[i]
        compute_edge_same(u, v, edge_res[i], scratch0, scratch1)

    # Compute edge 6 into scratch0 (its "same" flag); use scratch1 as the AND scratch.
    u6, v6 = edges[6]
    # inline OR-of-colors into scratch0 using scratch1 as double scratch is impossible
    # (need two scratch). So compute edge6 into scratch0 using scratch1 twice serially:
    def compute_edge_same_1scratch(u, v, out, scr):
        for t in (0, 1, 2):
            ucodes = color_indicator_terms(u, t)
            vcodes = color_indicator_terms(v, t)
            # need product of (u==t) and (v==t). Build (u==t) into scr, then for each
            # v-code do a triple control (scr & vcode-controlled ccx into out).
            for c in ucodes:
                apply_code_flags(u, c, scr)
            for c in vcodes:
                b0, b1 = qb(v)
                b0v, b1v = c
                pre = []
                if b0v == 0:
                    qc.x(b0); pre.append(b0)
                if b1v == 0:
                    qc.x(b1); pre.append(b1)
                qc.mcx([scr, b0, b1], out)
                for q in pre:
                    qc.x(q)
            for c in reversed(ucodes):
                apply_code_flags(u, c, scr)

    compute_edge_same_1scratch(u6, v6, scratch0, scratch1)

    # Now all 7 "same" flags live in edge_res[0..5] and scratch0.
    # f=1 iff all are 0. Apply phase -1 conditioned on all zero:
    # X all flags, multi-controlled Z, X back.
    flags = list(edge_res) + [scratch0]
    for q in flags:
        qc.x(q)
    qc.h(flags[-1])
    qc.mcx(flags[:-1], flags[-1])
    qc.h(flags[-1])
    for q in flags:
        qc.x(q)

    # Uncompute edge 6, then edges 5..0
    compute_edge_same_1scratch(u6, v6, scratch0, scratch1)
    for i in reversed(range(6)):
        u, v = edges[i]
        compute_edge_same(u, v, edge_res[i], scratch0, scratch1)
