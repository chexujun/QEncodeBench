from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (2, 4), (3, 4)]

    def qb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    a_edge = ancilla_qubits[0]   # per-edge "same color" flag
    a_all = ancilla_qubits[1]    # AND of "different" over all edges (target of phase)
    t0 = ancilla_qubits[2]
    t1 = ancilla_qubits[3]

    def edge_same(u, v, out, invert=False):
        # Set `out` ^= 1 iff decoded_color(u) == decoded_color(v).
        # Color decoding: c in {0,1,2}, with code 3 (b0=1,b1=1) -> color 0.
        # Equivalent color labels: color(u)==color(v) iff
        #   (both are color 0) OR (both color 1) OR (both color 2).
        # color0 code set S0 = {00, 11}; color1 = {01}; color2 = {10}.
        u0, u1 = qb(u)
        v0, v1 = qb(v)

        # Helper flags computed into t0 (for u) and t1 (for v):
        # We enumerate the three color-match cases and OR them into `out`.
        # Case color1: u code == 01 (u0=1,u1=0) AND v code == 01
        #   -> u0 & ~u1 & v0 & ~v1
        # Case color2: u code == 10 (u0=0,u1=1) AND v code == 10
        #   -> ~u0 & u1 & ~v0 & v1
        # Case color0: u in {00,11} AND v in {00,11}
        #   u_is0 = (u0==u1)  -> u0 XNOR u1 ;  v_is0 = (v0==v1)

        # --- Case color1: both codes 01 ---
        qc.x(u1); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], out)
        qc.x(u1); qc.x(v1)

        # --- Case color2: both codes 10 ---
        qc.x(u0); qc.x(v0)
        qc.mcx([u0, u1, v0, v1], out)
        qc.x(u0); qc.x(v0)

        # --- Case color0: u in {00,11} and v in {00,11} ---
        # compute u_is0 into t0: t0 = (u0 XNOR u1)
        qc.cx(u0, t0); qc.cx(u1, t0); qc.x(t0)  # t0 = 1 iff u0==u1
        qc.cx(v0, t1); qc.cx(v1, t1); qc.x(t1)  # t1 = 1 iff v0==v1
        qc.ccx(t0, t1, out)
        # uncompute t0,t1
        qc.x(t1); qc.cx(v1, t1); qc.cx(v0, t1)
        qc.x(t0); qc.cx(u1, t0); qc.cx(u0, t0)

    # Compute a_all = AND over edges of (colors differ) = AND of NOT same.
    # Strategy: for each edge set a_edge = same(edge); we want product of (1 - same).
    # Use: start with a_all in |0>, we mark it 1 iff ALL edges are "different".
    # Compute per-edge "different" flag = NOT same, AND them.
    # We do a multi-controlled X on a_all controlled on all edges being different.
    # Implement by computing a "same" flag per edge into distinct positions is not
    # possible (only limited ancillas). Instead: compute OR of all "same" into a_edge;
    # then colors-all-differ = NOT(a_edge). Phase -1 iff NOT(a_edge).

    # Compute a_edge = OR over edges of same(edge)
    for (u, v) in edges:
        edge_same(u, v, a_edge)

    # f = 1 iff a_edge == 0 (no monochromatic edge). Apply phase -1 when a_edge==0.
    qc.x(a_edge)
    qc.z(a_edge)
    qc.x(a_edge)

    # Uncompute a_edge (mirror)
    for (u, v) in reversed(edges):
        edge_same(u, v, a_edge)
