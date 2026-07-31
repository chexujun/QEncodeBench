from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 1), (0, 2), (0, 3), (1, 3), (2, 3)]

    def vqubits(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # For each edge, compute an ancilla = 1 iff the two endpoints have the SAME color.
    # Colors: c=0(00)->0, c=1(01)->1, c=2(10)->2, c=3(11)->0.
    # Two vertices u,v with bits (a0,a1) and (b0,b1) share a color iff:
    #   both decode to color 0: (a is 00 or 11) AND (b is 00 or 11)
    #   both color 1: a==01 and b==01
    #   both color 2: a==10 and b==10
    # We build "same-color" as OR of these 3 terms, into one edge-ancilla.
    #
    # We use dedicated ancillas. There are 5 edges and 6 ancillas.
    # Strategy: for each edge compute same[e] into edge_anc[e]; then the predicate
    # f = AND_e (NOT same[e]) = product of (1 - same_e). We phase when all edges are
    # properly colored, i.e. all edge-ancillas are 0.
    #
    # We compute all 5 edge-ancillas, then apply a phase of -1 when every edge-ancilla
    # is 0 (via X-wrapping + multi-controlled Z on the 5 edge ancillas using the 6th
    # ancilla as MCX target), then uncompute.

    edge_anc = ancilla_qubits[:5]
    helper = ancilla_qubits[5]

    def color0_flag(a0, a1, target):
        # set target ^= 1 iff (a0,a1) decodes to color 0, i.e. code 00 or 11
        # code00: a0=0,a1=0 ; code11: a0=1,a1=1 -> a0 == a1
        # a0==a1 iff NOT(a0 xor a1). Compute t = a0 xor a1 into target, then flip.
        qc.cx(a0, target)
        qc.cx(a1, target)
        qc.x(target)

    def color0_flag_un(a0, a1, target):
        qc.x(target)
        qc.cx(a1, target)
        qc.cx(a0, target)

    def compute_same(u, v, out):
        # out ^= same-color(u,v)
        ua0, ua1 = vqubits(u)
        va0, va1 = vqubits(v)
        # term color1: both == 01 (a0=1,a1=0)
        # controls: ua0=1, ua1=0, va0=1, va1=0
        qc.x(ua1); qc.x(va1)
        qc.mcx([ua0, ua1, va0, va1], out)
        qc.x(ua1); qc.x(va1)
        # term color2: both == 10 (a0=0,a1=1)
        qc.x(ua0); qc.x(va0)
        qc.mcx([ua0, ua1, va0, va1], out)
        qc.x(ua0); qc.x(va0)
        # term color0: both decode to color 0 (each code in {00,11})
        # Need flags f_u = (u is 00 or 11), f_v likewise, then out ^= f_u AND f_v.
        # Compute f_u into a temporary problem-independent ancilla? We only have
        # edge_anc/helper. Use helper for f_u and reuse... but helper is one qubit.
        # Instead compute f_u AND f_v directly: f_u = NOT(ua0 xor ua1), f_v = NOT(va0 xor va1).
        # Map each vertex so that "color0" becomes all-ones controllable.
        # Put xu = ua0 xor ua1 onto ua0 (in place), then color0 iff ua0==0.
        qc.cx(ua1, ua0)   # ua0 <- ua0 xor ua1 ; color0(u) iff ua0==0
        qc.cx(va1, va0)   # va0 <- va0 xor va1 ; color0(v) iff va0==0
        qc.x(ua0); qc.x(va0)
        qc.ccx(ua0, va0, out)   # out ^= color0(u) AND color0(v)
        qc.x(ua0); qc.x(va0)
        qc.cx(va1, va0)   # restore
        qc.cx(ua1, ua0)

    # compute all edge same-flags
    for e, (u, v) in enumerate(edges):
        compute_same(u, v, edge_anc[e])

    # phase -1 iff all edge_anc == 0  (properly colored)
    for q in edge_anc:
        qc.x(q)
    # multi-controlled Z on 5 edge ancillas: use helper as phase via mcp(pi)
    qc.h(helper)
    qc.mcx(edge_anc, helper)
    qc.h(helper)
    for q in edge_anc:
        qc.x(q)

    # uncompute edge same-flags (mirror)
    for e in reversed(range(len(edges))):
        u, v = edges[e]
        compute_same(u, v, edge_anc[e])
