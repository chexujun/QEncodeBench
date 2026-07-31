from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 4), (0, 5), (1, 2), (1, 3), (2, 4), (2, 5)]
    n = 6
    k = 4
    p = problem_qubits
    anc = ancilla_qubits

    # Ancilla layout:
    #   edge_flags[i] : one ancilla per edge (7) -> flags[i]=1 iff edge i covered
    #   We reuse: after computing all edge flags into 7 ancillas, we need an
    #   "all edges covered" AND. Then a count(<=4) check.
    # Total ancillas available: 10.
    # Plan:
    #   Use anc[0..6] (7) as edge-covered flags.
    #   Use anc[7] as "all_edges_covered" flag.
    #   Use anc[8] as "count_ok" (popcount <= 4) flag.
    #   Use anc[9] as scratch for count computation.
    #
    # count(x) <= 4  over 6 bits  <=>  NOT( count >= 5 )
    # count >= 5 means at least 5 of the 6 bits are 1, i.e. at most 1 zero.
    # Equivalent: the number of zero-bits z = 6 - count <= 1, i.e. z in {0,1}.
    # z==0 -> all six are 1. z==1 -> exactly one is 0 (five are 1).
    # So count>=5 iff (all six =1) OR (exactly one =0).
    # count_ok = NOT(count>=5). We'll compute bad = (count>=5) into anc[8],
    # then the phase is applied when all_edges_covered AND NOT bad.

    edge_anc = anc[0:7]
    all_edges = anc[7]
    bad_count = anc[8]
    scratch = anc[9]

    # ---- compute edge-covered flags ----
    # edge covered iff (p[u] OR p[v]) = NOT(NOT p[u] AND NOT p[v]).
    # flag = p[u] OR p[v]:  set flag=1 unless both are 0.
    # Compute via: x p[u]; x p[v]; ccx(p[u],p[v],flag)->flag=1 iff both zero;
    # x flag -> flag = OR; then restore p[u],p[v].
    def compute_or(u, v, out):
        qc.x(p[u]); qc.x(p[v])
        qc.ccx(p[u], p[v], out)
        qc.x(out)
        qc.x(p[u]); qc.x(p[v])

    def uncompute_or(u, v, out):
        qc.x(p[u]); qc.x(p[v])
        qc.x(out)
        qc.ccx(p[u], p[v], out)
        qc.x(p[u]); qc.x(p[v])

    for i, (u, v) in enumerate(edges):
        compute_or(u, v, edge_anc[i])

    # all_edges = AND of the 7 edge flags
    qc.mcx(edge_anc, all_edges)

    # ---- compute bad_count = (count of ones >= 5) ----
    # count>=5 iff all six are 1 (z==0) OR exactly one is 0 (z==1).
    # We compute this into bad_count using compute->...->uncompute internally.
    # Method: For "exactly one zero OR zero zeros" = "at most one zero".
    # at_most_one_zero over 6 bits.
    #
    # Build term "all six ones" and each "exactly bit j is zero, rest ones".
    # These 7 patterns are mutually exclusive, so bad_count = XOR (=OR here)
    # of their indicator ANDs. Use scratch to accumulate via CX from an
    # AND computed with mcx, uncomputing each pattern in turn.
    #
    # Pattern A: all ones -> mcx(all p, bad_count) toggles bad_count.
    qc.mcx(p, bad_count)
    # Patterns B_j: bit j = 0, all others = 1.
    # Indicator = (NOT p[j]) AND (AND_{m!=j} p[m]).
    # Implement: x p[j]; mcx(all p, bad_count); x p[j].
    for j in range(n):
        qc.x(p[j])
        qc.mcx(p, bad_count)
        qc.x(p[j])
    # Now bad_count = 1 iff (all ones) or (exactly one zero) = (count>=5).

    # ---- phase: mark iff all_edges AND NOT bad_count ----
    qc.x(bad_count)
    qc.h(scratch)
    qc.x(scratch)  # prepare |1> then H? Instead do multi-controlled Z directly.
    qc.x(scratch)
    qc.h(scratch)
    # (scratch restored to |0>; the above no-ops are removed by using mcp.)
    # Apply -1 phase controlled on (all_edges AND bad_count==0):
    qc.mcp(np.pi, [all_edges, bad_count], p[0])  # placeholder guard
    # Correct phase: controlled-Z on the two flags giving -1 when both are 1.
    # We want -1 when all_edges=1 and (NOT bad)=1. bad_count already X'd so
    # bad_count=1 means NOT bad. Use CZ between all_edges and bad_count:
    qc.cz(all_edges, bad_count)
    # remove the placeholder mcp effect:
    qc.mcp(-np.pi, [all_edges, bad_count], p[0])
    qc.x(bad_count)

    # ---- uncompute bad_count (mirror) ----
    for j in reversed(range(n)):
        qc.x(p[j])
        qc.mcx(p, bad_count)
        qc.x(p[j])
    qc.mcx(p, bad_count)

    # ---- uncompute all_edges ----
    qc.mcx(edge_anc, all_edges)

    # ---- uncompute edge flags (mirror) ----
    for i in reversed(range(len(edges))):
        u, v = edges[i]
        uncompute_or(u, v, edge_anc[i])
