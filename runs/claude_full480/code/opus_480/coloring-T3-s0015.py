from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4)]

    def qb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # ancilla[0..N-1] : per-edge "same color" flags (computed then uncomputed)
    # ancilla[3] : global AND result -> phase
    edge_flag = ancilla_qubits[0]
    a1 = ancilla_qubits[1]
    a2 = ancilla_qubits[2]
    result = ancilla_qubits[3]

    def compute_edge_same(u, v, flag):
        # flag ^= [color(u) == color(v)]
        # color(u)==color(v) iff the two vertices share a color in {0,1,2}
        # with the surjective decode 11->0 and 00->0 also color 0.
        # color0 set : codes {00, 11}; color1 : {01}; color2 : {10}.
        u0, u1 = qb(u)
        v0, v1 = qb(v)

        # is_color0(w) = (w0 AND w1) OR (NOT w0 AND NOT w1) = (w0 == w1)
        # compute into a1 for u, a2 for v using XNOR: a = NOT(w0 XOR w1)
        # both same color0:
        # We enumerate the three color-match cases and OR them onto flag.

        # ---- match color1: u==01 and v==01 : u0&~u1 & v0&~v1
        qc.x(u1); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], flag)
        qc.x(u1); qc.x(v1)

        # ---- match color2: u==10 and v==10 : ~u0&u1 & ~v0&v1
        qc.x(u0); qc.x(v0)
        qc.mcx([u0, u1, v0, v1], flag)
        qc.x(u0); qc.x(v0)

        # ---- match color0: u in {00,11} and v in {00,11}
        # is0(u) = (u0==u1) -> compute into a1 ; is0(v) -> a2 ; flag ^= a1&a2
        qc.cx(u0, a1); qc.cx(u1, a1); qc.x(a1)   # a1 = NOT(u0 xor u1) = (u0==u1)
        qc.cx(v0, a2); qc.cx(v1, a2); qc.x(a2)   # a2 = (v0==v1)
        qc.ccx(a1, a2, flag)
        # uncompute a1,a2
        qc.x(a2); qc.cx(v1, a2); qc.cx(v0, a2)
        qc.x(a1); qc.cx(u1, a1); qc.cx(u0, a1)

    def compute_edge_same_inv(u, v, flag):
        u0, u1 = qb(u)
        v0, v1 = qb(v)
        # mirror of compute_edge_same
        qc.cx(u0, a1); qc.cx(u1, a1); qc.x(a1)
        qc.cx(v0, a2); qc.cx(v1, a2); qc.x(a2)
        qc.ccx(a1, a2, flag)
        qc.x(a2); qc.cx(v1, a2); qc.cx(v0, a2)
        qc.x(a1); qc.cx(u1, a1); qc.cx(u0, a1)

        qc.x(u0); qc.x(v0)
        qc.mcx([u0, u1, v0, v1], flag)
        qc.x(u0); qc.x(v0)

        qc.x(u1); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], flag)
        qc.x(u1); qc.x(v1)

    # f(x)=1 iff NO edge is monochromatic, i.e. all edge_same flags are 0.
    # Compute each edge's "same" flag into a distinct scratch bit is limited;
    # instead: result = AND over edges of (NOT same_e).
    # Strategy: build a single flag that is OR of all "same" flags, phase when it is 0.
    # OR of same flags: accumulate into edge_flag by computing each edge same into
    # edge_flag but that XORs, not ORs. Use controlled accumulation with result bit.

    # We compute: result ^= (all edges different) by De Morgan.
    # Easier: set result=1, then for each edge, if that edge is "same", force
    # result to 0. Implement with: compute same_e into edge_flag, CX not needed;
    # We OR all same_e into edge_flag via sequential compute WITHOUT uncompute is
    # wrong (XOR). So do: for each edge, compute same_e into edge_flag, and CX
    # edge_flag-> we instead track OR using that same_e are mutually independent
    # but can both be 1.

    # Robust approach: OR accumulation into edge_flag using the identity
    # edge_flag_new = edge_flag OR same_e, done via:
    #   compute same_e into a fresh handling isn't available (only 1 scratch).
    # So use: result stays |0>; we phase-flip when edge_flag==0 using the fact
    # that XOR-accumulation equals OR only if at most one flag is 1 — not guaranteed.

    # Use multi-controlled OR via monochromatic-count parity is unsafe.
    # Therefore accumulate OR properly: for each edge compute same_e onto edge_flag
    # with a controlled scheme so edge_flag becomes sticky-1.

    # Sticky OR: edge_flag |= same_e  implemented as:
    #   compute same_e into a2-based temp already used inside; instead we use
    #   the pattern: X(edge_flag) then for each edge multiply (AND) the negations.
    # result = AND_e (NOT same_e). Compute NOT same_e sequentially by ANDing.

    # Initialize result = 1 (represents running AND of "different so far")
    qc.x(result)
    # For each edge, we need: result &= (NOT same_e).
    # result_new = result AND (NOT same_e).
    # Compute same_e into edge_flag, then apply: if same_e==1 set result=0.
    # result AND NOT same_e = result XOR (result AND same_e).
    # So: ccx(result, edge_flag, result) flips result to 0 when both 1 -> exactly
    # result &= NOT same_e (since if same_e=1: result^=result -> 0; if same_e=0: no change).
    for (u, v) in edges:
        compute_edge_same(u, v, edge_flag)
        qc.ccx(result, edge_flag, result)
        compute_edge_same_inv(u, v, edge_flag)

    # result == 1 iff all edges different -> f(x)=1. Phase it.
    qc.z(result)

    # Uncompute result back to |0>. Mirror the AND accumulation in reverse.
    for (u, v) in reversed(edges):
        compute_edge_same(u, v, edge_flag)
        qc.ccx(result, edge_flag, result)
        compute_edge_same_inv(u, v, edge_flag)
    qc.x(result)
