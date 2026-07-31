from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (3, 4)]

    def vq(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # edge ancillas: e_k = 1 iff edge k is SATISFIED (endpoints differ)
    edge_anc = ancilla_qubits[:len(edges)] if len(ancilla_qubits) >= len(edges) else None

    # We only have 5 ancillas but 8 edges. Compute edge-satisfaction into a
    # running AND accumulator using a reversible scheme with limited ancillas.
    # Strategy: use one "all-satisfied" flag ancilla built by successively
    # controlling on each edge's satisfaction, using temporary ancillas that
    # are computed and uncomputed per edge.

    flag = ancilla_qubits[0]          # counts number of UNsatisfied edges != 0 test
    t0 = ancilla_qubits[1]            # temp: color-equal indicator for an edge
    t1 = ancilla_qubits[2]            # temp helpers
    t2 = ancilla_qubits[3]
    t3 = ancilla_qubits[4]

    def color_equal_compute(u, v, out, h0, h1, h2):
        # colors of u and v equal, under surjective decode (11 -> color 0 == 00).
        # decode: color0 set S0 = {00, 11}, color1 = {01}, color2 = {10}.
        # u == v (as colors) iff (both in S0) or (u01 and v01) or (u10 and v10).
        ua0, ua1 = vq(u)
        va0, va1 = vq(v)
        # indicator u_in_S0 = (a0==a1)  -> compute into h0: h0 = NOT(a0 xor a1)
        qc.cx(ua0, h0); qc.cx(ua1, h0); qc.x(h0)          # h0 = (ua0==ua1)
        qc.cx(va0, h1); qc.cx(va1, h1); qc.x(h1)          # h1 = (va0==va1)
        # both in S0 -> term A into out
        qc.ccx(h0, h1, out)
        # uncompute h0,h1
        qc.x(h1); qc.cx(va1, h1); qc.cx(va0, h1)
        qc.x(h0); qc.cx(ua1, h0); qc.cx(ua0, h0)
        # term color1: u==01 and v==01 : ua0=1,ua1=0,va0=1,va1=0
        qc.x(ua1); qc.x(va1)
        qc.mcx([ua0, ua1, va0, va1], out)
        qc.x(ua1); qc.x(va1)
        # term color2: u==10 and v==10 : ua0=0,ua1=1,va0=0,va1=1
        qc.x(ua0); qc.x(va0)
        qc.mcx([ua0, ua1, va0, va1], out)
        qc.x(ua0); qc.x(va0)
        # now out = 1 iff colors equal (the three terms are mutually exclusive)

    # Compute: for each edge, set its "equal" temp, and toggle flag if equal.
    # flag accumulates parity of unsatisfied edges is NOT what we want; we want
    # flag = OR of (edge unsatisfied). Use flag as: flag stays 0 iff all edges
    # satisfied. Implement OR via De Morgan on a counter is hard with 1 qubit,
    # so instead build product of satisfaction into t3 using controlled chain.

    # We build "all_satisfied" into t3 by initializing t3=1 and ANDing each
    # edge's satisfaction (sat = NOT equal). AND accumulation needs the running
    # value plus each new bit -> Toffoli into a fresh target, but with limited
    # ancillas we recompute serially: use t3 as running AND stored, and for each
    # edge compute equal->t0, sat = not t0, and gate: new = running AND sat.
    # A reversible in-place AND-accumulate isn't a single gate; use the standard
    # trick: keep running AND in t3, combine with sat into flag then swap roles.
    # Simpler: mark phase = -1 iff ANY edge equal. Use flag = OR via multi-step.

    # Cleanest given budget: compute all 8 "equal" bits would need 8 ancillas.
    # Instead phase-kickback per edge is wrong (want AND, not per-edge phase).
    # Use nested compute of a single AND chain with 2 running ancillas.

    run = ancilla_qubits[0]   # running "all satisfied so far"
    tmp = ancilla_qubits[1]   # per-edge equal indicator
    h0 = ancilla_qubits[2]
    h1 = ancilla_qubits[3]
    nxt = ancilla_qubits[4]   # next running value

    ops = []  # record to uncompute in reverse

    # init run = 1
    qc.x(run); ops.append(('x', run))

    for (u, v) in edges:
        # compute tmp = colors_equal(u,v)
        color_equal_compute(u, v, tmp, h0, h1)
        # sat = NOT tmp ; nxt = run AND sat = run AND (NOT tmp)
        qc.x(tmp)                      # tmp = sat
        qc.ccx(run, tmp, nxt)          # nxt = run AND sat
        qc.x(tmp)                      # restore tmp = equal
        # uncompute tmp
        color_equal_uncompute(u, v, tmp, h0, h1)
        # move: run <- nxt, need run freed. Uncompute old run into 0 requires
        # knowing it; instead swap roles by relabeling via CX-based move:
        # copy nxt into a cleared run: first clear run using nxt and previous
        # relation is complex. To keep it correct and reversible we instead
        # accumulate differently below.
        raise RuntimeError
