import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 3), (1, 2), (1, 3), (2, 3)]

    def vq(v):
        # (low bit, high bit) for vertex v
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # We have 5 edges. For each edge we compute a "same-color" flag into an
    # edge-ancilla; f(x)=1 iff ALL edges are properly colored, i.e. NO edge
    # is monochromatic. We phase the state where every edge flag == 0.
    #
    # Colors: code c in {0,1,2,3}, with 3 -> color 0. So color(v):
    #   00 -> 0, 01 -> 1, 10 -> 2, 11 -> 0.
    # Two vertices u,v have the SAME color iff one of:
    #   both color 0: (u in {00,11}) and (v in {00,11})
    #   both color 1: u==01 and v==01
    #   both color 2: u==10 and v==10
    #
    # We build the "same color" predicate for an edge into an edge ancilla by
    # OR-ing these three cases (using an extra scratch ancilla), then combine.

    # ancilla layout: 5 edge-flag ancillas + 1 scratch
    edge_anc = ancilla_qubits[0:5]
    scratch = ancilla_qubits[5]

    def is_color0(u_low, u_high, anc, do):
        # color0 iff (low,high) in {00, 11}, i.e. low == high (XNOR)
        # anc ^= (low XNOR high) = NOT(low XOR high)
        do(u_low, anc)
        do(u_high, anc)
        qc.x(anc)

    def compute_edge_flag(u, v, flag):
        u_low, u_high = vq(u)
        v_low, v_high = vq(v)

        # Case both color 0: A = color0(u), B = color0(v) -> flag ^= A & B
        # Compute A into scratch:
        is_color0(u_low, u_high, scratch, qc.cx)
        # Need B = color0(v). Instead of another ancilla, we AND directly:
        # We want flag ^= color0(u) & color0(v).
        # Temporarily encode color0(v) by conditioning: use v's XNOR on the fly.
        # Build B into flag-adjacent? We only have scratch. So do nested:
        # Turn scratch into (color0(u) AND color0(v)) is not directly a single
        # gate, so we compute color0(v) into scratch2... but only one scratch.
        #
        # Alternative: mcx with controls being the raw qubits after mapping.
        # color0(u) & color0(v): controls = {u XNOR, v XNOR}. We have scratch =
        # color0(u). Compute color0(v) by flipping v_low^v_high onto... we need
        # a second scratch. Uncompute scratch and use direct multi-control on
        # transformed qubits instead.
        qc.x(scratch)
        is_color0(u_low, u_high, scratch, qc.cx)  # uncompute scratch back to 0

        # Direct approach: transform each vertex's low/high so that a chosen
        # color corresponds to all-ones on the two qubits, then mcx onto flag.

        # --- both color 0: color0 iff low==high. Map: set low' = low XOR high
        #     then color0 iff low'==0. Not all-ones friendly. Use: color0(u) is
        #     a function of 2 qubits with 2 minterms (00,11). We enumerate the
        #     same-color condition per edge as a sum of the pair-products below.

        # Same-color minterms over (u_low,u_high,v_low,v_high):
        #  color0 both: u in {00,11} x v in {00,11} -> 4 minterms
        #  color1 both: u=01 (low=1,high=0), v=01 -> 1 minterm
        #  color2 both: u=10 (low=0,high=1), v=10 -> 1 minterm
        minterms = []
        c0 = [(0, 0), (1, 1)]
        for (ul, uh) in c0:
            for (vl, vh) in c0:
                minterms.append((ul, uh, vl, vh))
        minterms.append((1, 0, 1, 0))  # color1 both
        minterms.append((0, 1, 0, 1))  # color2 both

        qubits = [u_low, u_high, v_low, v_high]
        for (a, b, c, d) in minterms:
            pattern = (a, b, c, d)
            zeros = [qubits[i] for i in range(4) if pattern[i] == 0]
            for z in zeros:
                qc.x(z)
            qc.mcx(qubits, flag)
            for z in zeros:
                qc.x(z)

    # Compute all edge flags
    for (u, v), flag in zip(edges, edge_anc):
        compute_edge_flag(u, v, flag)

    # f(x) = 1 iff all edge flags are 0. Phase when all edge_anc == 0:
    # Flip all flags, multi-controlled Z on all flags, flip back.
    for flag in edge_anc:
        qc.x(flag)
    qc.h(edge_anc[-1])
    qc.mcx(edge_anc[:-1], edge_anc[-1])
    qc.h(edge_anc[-1])
    for flag in edge_anc:
        qc.x(flag)

    # Uncompute all edge flags (mirror)
    for (u, v), flag in reversed(list(zip(edges, edge_anc))):
        compute_edge_flag(u, v, flag)
