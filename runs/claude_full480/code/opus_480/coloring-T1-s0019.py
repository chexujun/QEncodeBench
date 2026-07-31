from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 2), (0, 3), (0, 4), (1, 4)]

    def vq(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # For each edge, compute an ancilla = 1 iff the two endpoints have the SAME color.
    # Colors: c in {0,1,2}, with code 3 (11) also meaning color 0.
    # Two vertices u,v have same color iff:
    #   color(u)==color(v). Encode "is color 0" = (code==00 or code==11),
    #   "is color1" = code==01, "is color2" = code==10.
    # same_color = is0(u)&is0(v) | is1(u)&is1(v) | is2(u)&is2(v)
    #
    # f(x)=1 iff NO edge is monochromatic, i.e. all edge-ancillas are 0.
    # Multi-controlled Z on (all edge ancillas == 0) gives phase to the good states.
    # We compute each edge's "same_color" flag into a dedicated edge ancilla,
    # then apply a Z conditioned on all edge ancillas being 0 (X-sandwich + mcp/mcx),
    # then uncompute.

    edge_anc = ancilla_qubits[:len(edges)]

    def compute_same_color(u, v, target, work):
        # target ^= same_color(u,v); uses one work qubit, restored to 0.
        u0, u1 = vq(u)
        v0, v1 = vq(v)

        # ---- is1(u) & is1(v): code==01 -> b0=1,b1=0
        # is1 flag: b0 & ~b1
        # compute into work: work = is1(u) & is1(v)
        qc.x(u1); qc.x(v1)                     # now u1'=~b1u, v1'=~b1v
        qc.mcx([u0, u1], work)                 # work = b0u & ~b1u  (partial)
        # to AND with is1(v)=v0 & ~v1, use a nested approach:
        # Instead compute work2 chain. Simpler: build full term via ccx ladders.
        # Undo the partial and do proper 4-control into target via ancilla-free trick:
        qc.mcx([u0, u1], work)                 # undo
        qc.x(u1); qc.x(v1)                     # restore
        # Direct 4-controlled contributions into target using work as scratch:

        # term is1&is1: controls u0,~u1,v0,~v1
        qc.x(u1); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], target)
        qc.x(u1); qc.x(v1)

        # term is2&is2: is2 = ~b0 & b1 ; controls ~u0,u1,~v0,v1
        qc.x(u0); qc.x(v0)
        qc.mcx([u0, u1, v0, v1], target)
        qc.x(u0); qc.x(v0)

        # term is0&is0: is0 = (b1b0==00) or (11) = (b0 XNOR b1)... actually
        # is0 = ~(b0 XOR b1)  -> b0==b1. Compute p_u = (u0==u1), p_v=(v0==v1)
        # same0 = p_u & p_v. Use work to hold p_u == (u0 XNOR u1).
        qc.cx(u0, work); qc.cx(u1, work); qc.x(work)   # work = ~(u0 xor u1) = is0(u)
        # now need work & is0(v) into target: is0(v)= ~(v0 xor v1)
        # compute is0(v) into... need second scratch; reuse target control set:
        qc.cx(v0, target)  # placeholder -- not correct alone
        qc.cx(v0, target)  # undo placeholder
        # Instead: build is0(v) on-the-fly via X-controls is hard (parity). Use work only.
        # Put is0(v) also combined: temporarily compute is0(v) into another scratch bit
        # We have only one work here, so encode is0(v) into target-control via CCX using
        # a fresh trick: create p_v on 'work' too sequentially:
        # target ^= work & is0(v):
        #   compute is0(v) into a temp = we don't have; so use identity:
        #   work currently = is0(u). We AND with is0(v) using controlled parity:
        # Do: for target ^= is0(u)&is0(v), note is0(v)=~(v0 xor v1).
        # Use two CCX with control work and v-parity handled by flipping target on parity.
        # Approach: target ^= work  (when is0(v) true). Since is0(v)=~(v0 xor v1),
        # we gate 'work->target' by that parity using: 
        qc.x(work)  # work = ~is0(u) ... to revert we must be careful
        qc.x(work)  # revert (no-op pair) -- keep work = is0(u)
        # Controlled add: target ^= work AND (v0==v1)
        # Realize via: cx(v0->v1) making v1 = v0 xor v1 (=1 iff differ), then
        # ccx(work, v1_is_equal?) needs v1==0 for equal, so x(v1):
        qc.cx(v0, v1); qc.x(v1)                 # v1 now =1 iff v0==v1 (equal)
        qc.mcx([work, v1], target)              # target ^= is0(u) & is0(v)
        qc.x(v1); qc.cx(v0, v1)                 # restore v1

        # uncompute work (= is0(u))
        qc.x(work); qc.cx(u1, work); qc.cx(u0, work)

    work = ancilla_qubits[len(edges)]  # 5th ancilla as shared scratch

    for i, (u, v) in enumerate(edges):
        compute_same_color(u, v, edge_anc[i], work)

    # Phase: -1 iff all edge ancillas == 0 (no monochromatic edge).
    for a in edge_anc:
        qc.x(a)
    if len(edge_anc) == 1:
        qc.z(edge_anc[0])
    else:
        qc.h(edge_anc[-1])
        qc.mcx(edge_anc[:-1], edge_anc[-1])
        qc.h(edge_anc[-1])
    for a in edge_anc:
        qc.x(a)

    # Uncompute edge ancillas (mirror).
    for i in reversed(range(len(edges))):
        u, v = edges[i]
        compute_same_color(u, v, edge_anc[i], work)
