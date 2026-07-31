from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (0, 3), (1, 2), (1, 3)]

    def code_qubits(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # For each edge we compute a "same color" flag into an edge-ancilla.
    # Two vertices share a color iff their decoded colors are equal.
    # Decoding: 00->0, 01->1, 10->2, 11->0.  So codes u,w decode-equal iff:
    #   both in {00,11} (color 0), or u==w==01, or u==w==10.
    # Equivalently, treating color0 set S={00,11}:
    #   same iff (u in S and w in S) or (u==w and u in {01,10}).
    #
    # We build an edge flag e = 1 iff colors equal.  Use 2 work ancillas
    # per edge computation, released before next edge, plus one persistent
    # edge accumulator.  Budget: 5 ancillas.
    #
    # Strategy: flag_v0 (=1 iff vertex color==0) helpers, then combine.
    # Let A = ancilla[0], B = ancilla[1] used as scratch; edge result OR-ed.
    #
    # colors equal cases enumerated by (c_u, c_w) with decode:
    #   d(00)=0,d(11)=0,d(01)=1,d(10)=2
    # equal iff d(u)==d(w).
    #
    # We implement per edge: mark edge-monochromatic into scratch bit m,
    # accumulate: any monochromatic edge => f=0.  f=1 iff no edge mono.
    # We phase-flip states with f=1, i.e. NO edge monochromatic.
    #
    # Approach: compute m_edge for each edge into ancilla bits, then we want
    # phase -1 iff ALL m_edge == 0.  Use one accumulator: count mono edges.
    # Simpler: compute each mono flag into a distinct ancilla, apply a
    # multi-controlled phase that is -1 iff all four flags are 0 (controls
    # on |0>), then uncompute.

    b0 = [problem_qubits[2 * v] for v in range(4)]
    b1 = [problem_qubits[2 * v + 1] for v in range(4)]

    # helper: color-class predicates via decode.
    # color(v)=0 iff code in {00,11} iff b0==b1.
    # color(v)=1 iff code==01 iff (b0=1,b1=0).
    # color(v)=2 iff code==10 iff (b0=0,b1=1).
    #
    # Edge (u,w) monochromatic iff:
    #   (color u==0 and color w==0) or (u==01 and w==01) or (u==10 and w==10)
    # = (b0u==b1u and b0w==b1w) or (b0u&~b1u & b0w&~b1w)
    #   or (~b0u&b1u & ~b0w&b1w)
    #
    # We compute mono flag into an ancilla using compute->accumulate.

    def color0_flag(v, target, scratch):
        # target ^= 1 iff color(v)==0  (b0==b1)  == XNOR(b0,b1)
        qc.cx(b0[v], target)
        qc.cx(b1[v], target)
        qc.x(target)  # target ^= NOT(b0 xor b1) = XNOR

    def color0_flag_inv(v, target, scratch):
        qc.x(target)
        qc.cx(b1[v], target)
        qc.cx(b0[v], target)

    mono = ancilla_qubits[0:4]
    s = ancilla_qubits[4]  # scratch

    def compute_edge_mono(idx, u, w):
        m = mono[idx]
        # term1: color u==0 and color w==0
        # compute cu0 into s, then combine.
        # We accumulate the three OR terms into m via: m = t1 OR t2 OR t3.
        # OR of disjoint-ish terms; they can overlap? color0&color0 excludes
        # 01/10 cases, and the three terms are mutually exclusive, so OR = XOR.
        #
        # term1: cu0 AND cw0.  cu0 = XNOR(b0u,b1u), cw0 = XNOR(b0w,b1w).
        # Put cu0 on s, then need AND with cw0 -> use another temp; but only
        # one scratch. Instead compute cw0 on s, and use a controlled build:
        # We toggle m via ccx(cu0, cw0). Build cu0 on s first? need two.
        #
        # Use mcx with the raw code bits by adjusting with X gates.
        # term1 (both color0): XNOR pairs. Represent XNOR(b0,b1)=1 as parity.
        # Hard to AND two XNORs with mcx directly. So use scratch s for cw0,
        # and encode cu0 by temporarily flipping b0u so that cu0 == (b0u'==?).
        #
        # Simplify: compute s = cw0 = XNOR(b0w,b1w).
        qc.cx(b0[w], s); qc.cx(b1[w], s); qc.x(s)
        # now toggle m if cu0 AND s: cu0 = XNOR(b0u,b1u). We need AND of two
        # XNORs. Flip b0u,b1u trick: XNOR(b0u,b1u) = (b0u==b1u). We can map
        # to a single control by CX b1u->b0u? but that mutates problem qubit.
        # Instead use s2? none. Use m built via two ccx with case split:
        # XNOR(b0u,b1u)=1 in cases (00),(11). AND with s:
        #   ccx over (b0u=0,b1u=0,s): need X on b0u,b1u.
        qc.x(b0[u]); qc.x(b1[u])
        qc.mcx([b0[u], b1[u], s], m)   # case 00 & cw0
        qc.x(b0[u]); qc.x(b1[u])
        qc.mcx([b0[u], b1[u], s], m)   # case 11 & cw0
        # undo s
        qc.x(s); qc.cx(b1[w], s); qc.cx(b0[w], s)

        # term2: u==01 and w==01  -> b0=1,b1=0 both
        qc.x(b1[u]); qc.x(b1[w])
        qc.mcx([b0[u], b1[u], b0[w], b1[w]], m)
        qc.x(b1[u]); qc.x(b1[w])

        # term3: u==10 and w==10  -> b0=0,b1=1 both
        qc.x(b0[u]); qc.x(b0[w])
        qc.mcx([b0[u], b1[u], b0[w], b1[w]], m)
        qc.x(b0[u]); qc.x(b0[w])

    def uncompute_edge_mono(idx, u, w):
        m = mono[idx]
        qc.x(b0[u]); qc.x(b0[w])
        qc.mcx([b0[u], b1[u], b0[w], b1[w]], m)
        qc.x(b0[u]); qc.x(b0[w])

        qc.x(b1[u]); qc.x(b1[w])
        qc.mcx([b0[u], b1[u], b0[w], b1[w]], m)
        qc.x(b1[u]); qc.x(b1[w])

        qc.cx(b0[w], s); qc.cx(b1[w], s); qc.x(s)
        qc.x(b0[u]); qc.x(b1[u])
        qc.mcx([b0[u], b1[u], s], m)
        qc.x(b0[u]); qc.x(b1[u])
        qc.x(b0[u]); qc.x(b1[u])
        qc.mcx([b0[u], b1[u], s], m)
        qc.x(b0[u]); qc.x(b1[u])
        qc.x(s); qc.cx(b1[w], s); qc.cx(b0[w], s)

    # compute all edge mono flags
    for idx, (u, w) in enumerate(edges):
        compute_edge_mono(idx, u, w)

    # phase -1 iff all mono flags == 0  (controls on |0>)
    for m in mono:
        qc.x(m)
    qc.h(mono[3])
    qc.mcx([mono[0], mono[1], mono[2]], mono[3])
    qc.h(mono[3])
    for m in mono:
        qc.x(m)

    # uncompute in reverse order
    for idx, (u, w) in reversed(list(enumerate(edges))):
        uncompute_edge_mono(idx, u, w)
