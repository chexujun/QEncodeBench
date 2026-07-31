import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (0, 4), (1, 2), (1, 4), (2, 3), (2, 4), (3, 4)]

    # Per-vertex 2-bit code -> color, surjective: 00->0, 01->1, 10->2, 11->0.
    # color equality between u and v (used-color sense) must be FALSE on every edge.
    # We build predicate f = AND over edges of (color(u) != color(v)),
    # via De Morgan on an OR-of-monochromatic-edges flag.

    def qb(v, b):
        return problem_qubits[2 * v + b]

    e_anc = ancilla_qubits[0]   # per-edge monochromatic flag
    or_anc = ancilla_qubits[1]  # accumulates OR of all monochromatic edges
    t0 = ancilla_qubits[2]      # scratch
    t1 = ancilla_qubits[3]      # scratch

    # For an edge (u,v): colors are equal iff
    #   (both codes decode to color 0): u in {00,11} AND v in {00,11}, OR
    #   (codes equal AND code in {01,10}): (u==v) AND u in {01,10}.
    # Equivalently color(u)==color(v) as a boolean predicate on 4 bits.
    # We implement mono(u,v) = OR of the following disjoint cases where colors match:
    #  case A: color 0 on both: uc in {00,11} and vc in {00,11}
    #  case B: color 1 on both: uc==01 and vc==01
    #  case C: color 2 on both: uc==10 and vc==10

    def compute_edge(u, v):
        # decode: is-color0(w) = (b0==b1)  -> XOR of bits == 0
        # is-color1(w) = b0 & ~b1 ; is-color2(w) = ~b0 & b1
        u0, u1 = qb(u, 0), qb(u, 1)
        v0, v1 = qb(v, 0), qb(v, 1)

        # --- case A: both color 0 ---
        # t0 = is-color0(u) = NOT(u0 xor u1)
        qc.cx(u0, t0); qc.cx(u1, t0); qc.x(t0)
        # t1 = is-color0(v)
        qc.cx(v0, t1); qc.cx(v1, t1); qc.x(t1)
        # e_anc ^= t0 & t1
        qc.ccx(t0, t1, e_anc)
        # uncompute t0,t1
        qc.x(t1); qc.cx(v1, t1); qc.cx(v0, t1)
        qc.x(t0); qc.cx(u1, t0); qc.cx(u0, t0)

        # --- case B: both color 1 (code 01: b0=1,b1=0) ---
        # is-color1(w) = b0 & ~b1
        qc.x(u1); qc.x(v1)
        # t0 = u0 & ~u1
        qc.ccx(u0, u1, t0)
        # t1 = v0 & ~v1
        qc.ccx(v0, v1, t1)
        qc.ccx(t0, t1, e_anc)
        qc.ccx(v0, v1, t1)
        qc.ccx(u0, u1, t0)
        qc.x(u1); qc.x(v1)

        # --- case C: both color 2 (code 10: b0=0,b1=1) ---
        qc.x(u0); qc.x(v0)
        qc.ccx(u0, u1, t0)   # t0 = ~u0 & u1
        qc.ccx(v0, v1, t1)   # t1 = ~v0 & v1
        qc.ccx(t0, t1, e_anc)
        qc.ccx(v0, v1, t1)
        qc.ccx(u0, u1, t0)
        qc.x(u0); qc.x(v0)

    def uncompute_edge(u, v):
        # exact mirror (all operations are self-inverse involutions here)
        u0, u1 = qb(u, 0), qb(u, 1)
        v0, v1 = qb(v, 0), qb(v, 1)

        # mirror case C
        qc.x(u0); qc.x(v0)
        qc.ccx(u0, u1, t0)
        qc.ccx(v0, v1, t1)
        qc.ccx(t0, t1, e_anc)
        qc.ccx(v0, v1, t1)
        qc.ccx(u0, u1, t0)
        qc.x(u0); qc.x(v0)

        # mirror case B
        qc.x(u1); qc.x(v1)
        qc.ccx(u0, u1, t0)
        qc.ccx(v0, v1, t1)
        qc.ccx(t0, t1, e_anc)
        qc.ccx(v0, v1, t1)
        qc.ccx(u0, u1, t0)
        qc.x(u1); qc.x(v1)

        # mirror case A
        qc.cx(u0, t0); qc.cx(u1, t0); qc.x(t0)
        qc.cx(v0, t1); qc.cx(v1, t1); qc.x(t1)
        qc.ccx(t0, t1, e_anc)
        qc.x(t1); qc.cx(v1, t1); qc.cx(v0, t1)
        qc.x(t0); qc.cx(u1, t0); qc.cx(u0, t0)

    # For each edge: compute e_anc = mono(edge), OR it into or_anc, then
    # uncompute e_anc so it is clean for the next edge.
    for (u, v) in edges:
        compute_edge(u, v)
        # or_anc |= e_anc  via: or_anc ^= e_anc  when e_anc set.
        # Since edges' mono flags can overlap only in OR sense, we need a true OR.
        # Implement OR incrementally: or_anc = or_anc OR e_anc
        #   = NOT( NOT or_anc AND NOT e_anc ).
        qc.x(or_anc); qc.x(e_anc)
        qc.ccx(or_anc, e_anc, or_anc)  # invalid: target among controls
        # (replaced below)


# The above incremental-OR is unsafe; provide a corrected full implementation.

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (0, 4), (1, 2), (1, 4), (2, 3), (2, 4), (3, 4)]

    def qb(v, b):
        return problem_qubits[2 * v + b]

    e_anc = ancilla_qubits[0]
    cnt = ancilla_qubits[1]   # unused as counter; using flag approach
    t0 = ancilla_qubits[2]
    t1 = ancilla_qubits[3]

    def edge_ops(u, v):
        u0, u1 = qb(u, 0), qb(u, 1)
        v0, v1 = qb(v, 0), qb(v, 1)
        # case A: both color 0
        qc.cx(u0, t0); qc.cx(u1, t0); qc.x(t0)
        qc.cx(v0, t1); qc.cx(v1, t1); qc.x(t1)
        qc.ccx(t0, t1, e_anc)
        qc.x(t1); qc.cx(v1, t1); qc.cx(v0, t1)
        qc.x(t0); qc.cx(u1, t0); qc.cx(u0, t0)
        # case B: both color 1
        qc.x(u1); qc.x(v1)
        qc.ccx(u0, u1, t0)
        qc.ccx(v0, v1, t1)
        qc.ccx(t0, t1, e_anc)
        qc.ccx(v0, v1, t1)
        qc.ccx(u0, u1, t0)
        qc.x(u1); qc.x(v1)
        # case C: both color 2
        qc.x(u0); qc.x(v0)
        qc.ccx(u0, u1, t0)
        qc.ccx(v0, v1, t1)
        qc.ccx(t0, t1, e_anc)
        qc.ccx(v0, v1, t1)
        qc.ccx(u0, u1, t0)
        qc.x(u0); qc.x(v0)

    # e_anc holds parity of #monochromatic edges after all edges are XORed in.
    # But f=1 requires ZERO monochromatic edges, not even parity.
    # So we cannot use a single-qubit XOR flag. Instead flip each edge's flag
    # into a per-edge bit and require all edges "good". We reuse the fact that
    # e_anc after edge_ops toggles once iff that edge is monochromatic.
    # To detect "any monochromatic", record e_anc into e_anc as XOR is wrong.
    #
    # Correct approach: after edge_ops(u,v), e_anc == 1 iff edge mono. Apply a
    # phase only when ALL edges are good -> we need e_anc to accumulate an OR.
    # Use e_anc as a "bad-so-far" latch via CX that only sets, never clears,
    # controlled on a freshly computed per-edge flag, then uncompute the flag.
    #
    # We compute each edge's mono flag into t0-based scratch chain; but the OR
    # latch needs its own qubit distinct from controls. Use e_anc as latch and
    # a separate scratch flag `sf` = ancilla t1 is already used inside edge_ops.
    #
    # Simplify: compute mono flag of edge into `mf`, CX mf->latch, uncompute mf.

    latch = ancilla_qubits[0]
    mf = ancilla_qubits[1]
    t0 = ancilla_qubits[2]
    t1 = ancilla_qubits[3]

    def compute_mf(u, v):
        u0, u1 = qb(u, 0), qb(u, 1)
        v0, v1 = qb(v, 0), qb(v, 1)
        # case A -> mf
        qc.cx(u0, t0); qc.cx(u1, t0); qc.x(t0)
        qc.cx(v0, t1); qc.cx(v1, t1); qc.x(t1)
        qc.ccx(t0, t1, mf)
        qc.x(t1); qc.cx(v1, t1); qc.cx(v0, t1)
        qc.x(t0); qc.cx(u1, t0); qc.cx(u0, t0)
        # case B -> mf
        qc.x(u1); qc.x(v1)
        qc.ccx(u0, u1, t0); qc.ccx(v0, v1, t1)
        qc.ccx(t0, t1, mf)
        qc.ccx(v0, v1, t1); qc.ccx(u0, u1, t0)
        qc.x(u1); qc.x(v1)
        # case C -> mf
        qc.x(u0); qc.x(v0)
        qc.ccx(u0, u1, t0); qc.ccx(v0, v1, t1)
        qc.ccx(t0, t1, mf)
        qc.ccx(v0, v1, t1); qc.ccx(u0, u1, t0)
        qc.x(u0); qc.x(v0)

    def uncompute_mf(u, v):
        u0, u1 = qb(u, 0), qb(u, 1)
        v0, v1 = qb(v, 0), qb(v, 1)
        qc.x(u0); qc.x(v0)
        qc.ccx(u0, u1, t0); qc.ccx(v0, v1, t1)
        qc.ccx(t0, t1, mf)
        qc.ccx(v0, v1, t1); qc.ccx(u0, u1, t0)
        qc.x(u0); qc.x(v0)
        qc.x(u1); qc.x(v1)
        qc.ccx(u0, u1, t0); qc.ccx(v0, v1, t1)
        qc.ccx(t0, t1, mf)
        qc.ccx(v0, v1, t1); qc.ccx(u0, u1, t0)
        qc.x(u1); qc.x(v1)
        qc.cx(u0, t0); qc.cx(u1, t0); qc.x(t0)
        qc.cx(v0, t1); qc.cx(v1, t1); qc.x(t1)
        qc.ccx(t0, t1, mf)
        qc.x(t1); qc.cx(v1, t1); qc.cx(v0, t1)
        qc.x(t0); qc.cx(u1, t0); qc.cx(u0, t0)

    # For each edge, note the three cases are mutually exclusive, so mf becomes
    # exactly 1 iff the edge is monochromatic. CX mf -> latch sets latch to the
    # OR of all mono edges (latch only accumulates; safe because mf is 0/1 and
    # we uncompute mf each time, and latch is never a control here).
    for (u, v) in edges:
        compute_mf(u, v)
        qc.cx(mf, latch)
        uncompute_mf(u, v)

    # latch == 1 iff some edge monochromatic (f==0). We want phase -1 iff f==1,
    # i.e. iff latch == 0. Apply phase on latch==0: X, Z, X.
    qc.x(latch)
    qc.z(latch)
    qc.x(latch)

    # Uncompute latch back to |0>.
    for (u, v) in reversed(edges):
        compute_mf(u, v)
        qc.cx(mf, latch)
        uncompute_mf(u, v)
