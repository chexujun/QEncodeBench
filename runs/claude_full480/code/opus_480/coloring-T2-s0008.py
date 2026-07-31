from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)]

    def vq(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # We need one ancilla per edge to record "edge OK" (colors differ),
    # then a multi-controlled phase when all edges are OK.
    edge_anc = ancilla_qubits[:len(edges)]      # 5 ancillas
    tmp = ancilla_qubits[len(edges)]            # 1 scratch ancilla

    def decode_equal_compute(u, v, target):
        # Set target = 1 iff decoded_color(u) == decoded_color(v).
        # Colors: c in {0,1,2}, with code 3 (11) mapping to color 0.
        # Equivalently color(u)==color(v) iff:
        #   both codes equal, OR one code is 00 and other is 11, OR one is 11 and other 00.
        # That is: codes agree after mapping 11->00.
        # Map: effective (a0,a1) where if (b0,b1)==(1,1) treat as (0,0).
        # color equal iff effective codes identical.
        u0, u1 = vq(u)
        v0, v1 = vq(v)

        # Compute effective bits into fresh scratch is expensive; instead
        # directly test equality of colors via the "monochromatic" condition.
        # color(u)==color(v) == 1 iff for the pair of 2-bit codes they land
        # on same color. Enumerate matching code-pairs is brute force; avoid.
        #
        # Use logic: define for each vertex m0,m1 = code bits, and note
        # color==0 iff code in {00,11} i.e. (m0==m1). color==1 iff code==01
        # (m0=1,m1=0). color==2 iff code==10 (m0=0,m1=1).
        #
        # colors equal iff:
        #   (u is color0 and v is color0) or
        #   (u code==01 and v code==01) or
        #   (u code==10 and v code==10)
        #
        # We build three "both same specific color" terms and OR them into target.
        #
        # Term A: both color0: (u0==u1) and (v0==v1).
        #   pu = NOT(u0 xor u1); pv = NOT(v0 xor v1); A = pu and pv.
        # Term B: both color1 (code 01: m0=1,m1=0): (u0 and not u1) and (v0 and not v1).
        # Term C: both color2 (code 10: m0=0,m1=1): (not u0 and u1) and (not v0 and v1).

        # --- Term A: both color 0 ---
        # pu into u-scratch? use tmp qubit chain carefully. We only have one tmp.
        # Instead we compute each term's contribution directly onto `target`
        # using ancilla-free multi-controlled X with control-state modifiers (X wraps).

        # Term A: control on (u0==u1) and (v0==v1).
        # (u0==u1) means u0 xor u1 == 0. Put parity into tmp.
        qc.cx(u0, tmp); qc.cx(u1, tmp)   # tmp = u0 xor u1
        qc.cx(v0, tmp)                    # careful: need separate; do sequentially below instead
        qc.cx(v0, tmp)                    # undo (no-op placeholder) -> revert
        qc.cx(u1, tmp); qc.cx(u0, tmp)   # tmp back to 0

        # The above inline approach is fragile; use explicit gate sequence:
        pass

    # Robust construction: compute per-edge "equal" flag with a clean routine.
    def edge_equal(u, v, target):
        u0, u1 = vq(u); v0, v1 = vq(v)
        # Term A (both color 0): X on u0,u1,v0,v1 controls with parity trick.
        # both color0 = (u0 XNOR u1) AND (v0 XNOR v1)
        # Compute pu = u0 XNOR u1 into tmp: tmp starts 0.
        qc.cx(u0, tmp); qc.cx(u1, tmp); qc.x(tmp)        # tmp = NOT(u0 xor u1)=pu
        # Now need pv AND pu -> target. Compute pv on the fly via controls:
        # We want target ^= pu AND pv. pv=(v0 XNOR v1). Use v0,v1 with X-conditioning:
        # target ^= pu & (v0==v1). Realize (v0==v1) as: apply for both v==00 and v==11.
        # v==00: controls v0=0,v1=0 => X v0,v1 then ccx-like.
        qc.x(v0); qc.x(v1)
        qc.mcx([tmp, v0, v1], target)
        qc.x(v0); qc.x(v1)
        # v==11:
        qc.mcx([tmp, v0, v1], target)
        qc.x(tmp); qc.cx(u1, tmp); qc.cx(u0, tmp)        # uncompute tmp back to 0

        # Term B (both color1, code01: m0=1,m1=0): (u0 & ~u1) & (v0 & ~v1)
        qc.x(u1); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], target)
        qc.x(u1); qc.x(v1)

        # Term C (both color2, code10: m0=0,m1=1): (~u0 & u1) & (~v0 & v1)
        qc.x(u0); qc.x(v0)
        qc.mcx([u0, u1, v0, v1], target)
        qc.x(u0); qc.x(v0)

    # Compute each edge's "equal" (monochromatic) flag into its ancilla.
    for (u, v), anc in zip(edges, edge_anc):
        edge_equal(u, v, anc)

    # f(x)=1 iff NO edge is monochromatic, i.e. all edge_equal flags are 0.
    # Phase -1 when all edge_anc == 0: flip them, mcp(pi), flip back.
    for anc in edge_anc:
        qc.x(anc)
    qc.h(edge_anc[-1])
    qc.mcx(edge_anc[:-1], edge_anc[-1])
    qc.h(edge_anc[-1])
    for anc in edge_anc:
        qc.x(anc)

    # Uncompute the edge flags (mirror).
    for (u, v), anc in zip(reversed(edges), reversed(edge_anc)):
        edge_equal(u, v, anc)
