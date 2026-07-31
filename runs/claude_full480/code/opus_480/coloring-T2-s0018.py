from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3)]

    def code_qubits(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # ancilla layout: one "edge-ok" ancilla per edge (5), plus one flip ancilla
    edge_anc = ancilla_qubits[:5]
    flip = ancilla_qubits[5]

    def apply_x_pattern(qb, code, target_c):
        # decode: color(c) with c in {0,1,2}, c=3 -> color 0
        # We need equality of decoded colors. Represent each vertex's decoded
        # color as a 2-bit value d in {0,1,2}. Then edge ok iff d_u != d_v.
        pass

    # We compute, for each vertex, a normalized 2-bit color into scratch.
    # But to save ancillas we instead directly test monochromaticity per edge
    # using controlled logic over the raw code bits.
    #
    # Decoded color equality between vertices u,v.
    # code c: 00->0, 01->1, 10->2, 11->0. So decoded color d = c if c<3 else 0.
    # Equivalently d==0 iff c in {00,11}; d==1 iff c==01; d==2 iff c==10.
    #
    # Edge monochromatic iff (d_u==0 and d_v==0) or (d_u==1 and d_v==1)
    #                        or (d_u==2 and d_v==2).
    #
    # For each vertex define predicates on its 2 code bits (b0 low, b1 high):
    #   P0 = (~b0 & ~b1) | (b0 & b1)  = XNOR(b0,b1)   -> color 0
    #   P1 = b0 & ~b1                                  -> color 1
    #   P2 = ~b0 & b1                                  -> color 2
    #
    # edge_ok = NOT monochromatic. We want edge_anc[e] = 1 iff edge ok.
    # Build monochromatic = P0u&P0v | P1u&P1v | P2u&P2v, set edge_anc=NOT that.
    #
    # To keep ancilla usage low we compute monochromatic into edge_anc[e]
    # (as OR of three AND-terms) using multi-controlled-X gates with
    # controls put into the correct polarity via X gates, then invert.

    def mono_term(u, v, sel, target):
        # sel in {0,1,2}; flip control polarities so that MCX fires exactly
        # when both vertices have decoded color == sel.
        bu0, bu1 = code_qubits(u)
        bv0, bv1 = code_qubits(v)
        if sel == 1:
            # P1 = b0 & ~b1 : need b0=1,b1=0
            ctrls = [(bu0, 1), (bu1, 0), (bv0, 1), (bv1, 0)]
            for q, pol in ctrls:
                if pol == 0:
                    qc.x(q)
            qc.mcx([bu0, bu1, bv0, bv1], target)
            for q, pol in ctrls:
                if pol == 0:
                    qc.x(q)
        elif sel == 2:
            # P2 = ~b0 & b1 : need b0=0,b1=1
            ctrls = [(bu0, 0), (bu1, 1), (bv0, 0), (bv1, 1)]
            for q, pol in ctrls:
                if pol == 0:
                    qc.x(q)
            qc.mcx([bu0, bu1, bv0, bv1], target)
            for q, pol in ctrls:
                if pol == 0:
                    qc.x(q)
        else:
            # P0 = XNOR(b0,b1) : color 0 when code is 00 or 11.
            # Both vertices color 0 iff (bu0==bu1) and (bv0==bv1) and match.
            # Decompose into the two concrete matching cases:
            #   both 00: bu0=0,bu1=0,bv0=0,bv1=0
            #   both 11: bu0=1,bu1=1,bv0=1,bv1=1
            # But we also need the MIXED cases where one is 00 and other is 11
            # (still both color 0 -> monochromatic). Enumerate all 4 combos.
            for (cu, cv) in [((0, 0), (0, 0)), ((0, 0), (1, 1)),
                             ((1, 1), (0, 0)), ((1, 1), (1, 1))]:
                pols = [(bu0, cu[0]), (bu1, cu[1]),
                        (bv0, cv[0]), (bv1, cv[1])]
                for q, pol in pols:
                    if pol == 0:
                        qc.x(q)
                qc.mcx([bu0, bu1, bv0, bv1], target)
                for q, pol in pols:
                    if pol == 0:
                        qc.x(q)

    def compute_edge_ok(e):
        u, v = edges[e]
        t = edge_anc[e]
        # t currently |0>. Set t = monochromatic(u,v) via XOR of disjoint terms.
        # The terms for sel=0,1,2 are mutually exclusive across basis states,
        # so XOR-accumulation equals OR.
        mono_term(u, v, 0, t)
        mono_term(u, v, 1, t)
        mono_term(u, v, 2, t)
        # Now t = 1 iff monochromatic. edge_ok = NOT t -> invert.
        qc.x(t)

    def uncompute_edge_ok(e):
        u, v = edges[e]
        t = edge_anc[e]
        qc.x(t)
        mono_term(u, v, 2, t)
        mono_term(u, v, 1, t)
        mono_term(u, v, 0, t)

    # Compute all edge_ok ancillas.
    for e in range(5):
        compute_edge_ok(e)

    # f(x)=1 iff all edges ok -> all edge_anc == 1. Phase flip via MCZ.
    qc.h(flip)
    qc.mcx(edge_anc, flip)
    qc.h(flip)

    # Uncompute edge_ok ancillas.
    for e in reversed(range(5)):
        uncompute_edge_ok(e)
