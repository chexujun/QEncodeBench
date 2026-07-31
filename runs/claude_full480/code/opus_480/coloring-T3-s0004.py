from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Vertex v uses qubits (b0, b1) = problem_qubits[2v], problem_qubits[2v+1]
    # code c = b0 + 2*b1 ; colors: 0->0,1->1,2->2,3->0 (surjective)
    # Edge (u,v) is SATISFIED iff color(u) != color(v).
    # f(x)=1 iff ALL edges satisfied. We use 3 ancillas as edge-conflict
    # accumulators via the "each edge OK" AND, computed by marking conflicts.
    #
    # Strategy: for each edge, compute a "conflict" bit (=1 iff colors equal)
    # into a fresh scratch ancilla, OR-accumulate is hard; instead we count:
    # f = AND over edges of (NOT conflict_e). We compute NO-conflict per edge
    # into ancilla a0 as a running AND is also awkward with reuse.
    #
    # Cleanest correct approach: multi-controlled phase over the predicate
    # "no edge is monochromatic". We build it as: temporarily set an ancilla
    # a_all to 1, then for each edge AND-in (colors differ). But AND-in
    # requires the per-edge predicate as a single control line.
    #
    # We implement per-edge "colors differ" predicate P_e directly as a
    # controlled operation onto a target using the fact that with 3 colors
    # encoded in 2 bits (with 3==0), color(u)==color(v) is a boolean function
    # of the 4 bits (u0,u1,v0,v1). We compute conflict_e into scratch and
    # accumulate the phase using the standard technique:
    #
    #   f = 1  iff  sum_e conflict_e == 0.
    #
    # We compute each conflict into a dedicated scratch qubit, but only have
    # 4 ancillas. So we compute conflicts one edge at a time into a0, and
    # keep a running "all_ok" flag in a1 using compute/uncompute nesting is
    # complex. Instead: accumulate the NUMBER of conflicts is not needed —
    # we need AND of (no conflict). Equivalent: phase -1 iff NONE of the
    # conflict bits is set. Using De Morgan with an OR into one ancilla:
    #
    #   conflict_any = OR_e conflict_e   (into a0)
    #   phase -1 iff conflict_any == 0   -> Z sandwiched by X on a0
    #
    # OR is accumulated by XOR-free method: set a0=1 whenever any edge
    # conflicts. But OR of overlapping terms needs care to uncompute.
    # We instead compute conflict_e into a fresh scratch a1, CX it is XOR
    # not OR. To get OR safely and reversibly we use: a0 stays the OR by
    # multi-controlled-X per edge onto a0 controlled on conflict pattern,
    # which is monotone (only sets a0 to 1), and uncomputes exactly by
    # replaying the same gates in reverse (they are self-inverse MCX).

    a_conf = ancilla_qubits[0]   # per-edge conflict scratch (returned to 0)
    a_or = ancilla_qubits[1]     # OR of all conflicts
    a_t = ancilla_qubits[2]      # scratch for equality subterms

    edges = [(0, 2), (0, 4), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]

    def q(v, b):
        return problem_qubits[2 * v + b]

    # color(u)==color(v). With codes cu,cv in {00,01,10,11}, mapping 11->00.
    # Equality of colors holds iff:
    #   (cu==cv exactly)  OR  (one is 00 and other is 11) OR (one is 11 and other is 00)
    # i.e. equal-as-color = (cu==cv) OR ({cu,cv}=={00,11}).
    # Let A = both bits equal: (u0==v0) AND (u1==v1)  -> exact code equality.
    # Let B = cu,cv are 00 and 11 in some order:
    #    (u==00 and v==11) or (u==11 and v==00).
    # conflict = A OR B. A and B are mutually exclusive, so conflict = A XOR B.

    def compute_conflict(u, v):
        u0, u1, v0, v1 = q(u, 0), q(u, 1), q(v, 0), q(v, 1)
        # --- term A: exact equality of two 2-bit codes ---
        # eq_bit0 = NOT(u0 XOR v0), eq_bit1 = NOT(u1 XOR v1)
        # A = eq_bit0 AND eq_bit1. Compute into a_conf using a_t as helper.
        qc.cx(u0, v0)           # v0 = u0 xor v0  (0 iff equal)
        qc.cx(u1, v1)           # v1 = u1 xor v1
        qc.x(v0)
        qc.x(v1)                # now v0,v1 =1 iff respective bits equal
        qc.ccx(v0, v1, a_conf)  # a_conf = A (exact code equality)
        # --- term B: {00,11} pair -> both eq_bits are 0 in original? no.
        # Rebuild B from the same transformed data:
        # u==00 & v==11  OR  u==11 & v==00.
        # In transformed coords this is messy; restore first, do B on a_t,
        # then xor into a_conf.
        qc.x(v0)
        qc.x(v1)
        qc.cx(u1, v1)
        qc.cx(u0, v0)           # v0,v1 restored to original code bits
        # B into a_t: pattern1 u=00,v=11 ; pattern2 u=11,v=00
        # u=00 : u0=0,u1=0 ; v=11 : v0=1,v1=1
        qc.x(u0); qc.x(u1)
        qc.mcx([u0, u1, v0, v1], a_t)   # u0!u1! & v0 v1
        qc.x(u0); qc.x(u1)
        # u=11,v=00
        qc.x(v0); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], a_t)   # u0 u1 & v0! v1!
        qc.x(v0); qc.x(v1)
        # a_conf = A XOR B  (A,B mutually exclusive)
        qc.cx(a_t, a_conf)
        # uncompute a_t (replay B, self-inverse)
        qc.x(v0); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], a_t)
        qc.x(v0); qc.x(v1)
        qc.x(u0); qc.x(u1)
        qc.mcx([u0, u1, v0, v1], a_t)
        qc.x(u0); qc.x(u1)
        # a_t now back to 0. a_conf holds conflict for edge (u,v).

    def uncompute_conflict(u, v):
        u0, u1, v0, v1 = q(u, 0), q(u, 1), q(v, 0), q(v, 1)
        # exact reverse of compute_conflict for a_conf (a_t already clean)
        qc.x(u0); qc.x(u1)
        qc.mcx([u0, u1, v0, v1], a_t)
        qc.x(u0); qc.x(u1)
        qc.x(v0); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], a_t)
        qc.x(v0); qc.x(v1)
        qc.cx(a_t, a_conf)
        qc.x(v0); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], a_t)
        qc.x(v0); qc.x(v1)
        qc.x(u0); qc.x(u1)
        qc.mcx([u0, u1, v0, v1], a_t)
        qc.x(u0); qc.x(u1)
        qc.cx(u0, v0)
        qc.cx(u1, v1)
        qc.x(v0)
        qc.x(v1)
        qc.ccx(v0, v1, a_conf)
        qc.x(v0)
        qc.x(v1)
        qc.cx(u1, v1)
        qc.cx(u0, v0)

    # OR-accumulate conflicts into a_or (monotone MCX per edge).
    for (u, v) in edges:
        compute_conflict(u, v)
        qc.cx(a_conf, a_or)       # a_or |= conflict (safe: at most sets bit)
        uncompute_conflict(u, v)

    # f = 1 iff a_or == 0 (no conflicts). Phase -1 on a_or==0.
    qc.x(a_or)
    qc.z(a_or)
    qc.x(a_or)

    # Uncompute a_or by replaying the OR accumulation in reverse.
    for (u, v) in reversed(edges):
        compute_conflict(u, v)
        qc.cx(a_conf, a_or)
        uncompute_conflict(u, v)
