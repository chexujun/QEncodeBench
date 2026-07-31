from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0,1),(0,4),(0,5),(1,3),(1,4),(2,3),(2,4),(3,5)]

    def qb(v):
        return problem_qubits[2*v], problem_qubits[2*v+1]

    # ancilla layout: a_edge = ancilla_qubits[0] flags "this edge is monochromatic"
    # e0..e3 = ancilla_qubits[1..4] hold per-edge equality-of-color bits
    a_edge = ancilla_qubits[0]
    edge_flags = ancilla_qubits[1:5]  # 4 available

    # For an edge (u,v): decoded colors equal iff the two vertices map to the same
    # color under surjective decode (00->0,01->1,10->2,11->0).
    # Color-equal predicate EQ(u,v) as a boolean over 4 bits u0,u1,v0,v1:
    #   color(u)=color(v).
    # We compute EQ into a flag ancilla f using a small sum-of-minterms with
    # compute/uncompute so f returns clean, but we need f set (not toggled back)
    # until after the phase.  Strategy: compute all edge flags, count how many
    # edges are monochromatic into parity? No: f(x)=1 iff NO edge monochromatic,
    # i.e. AND over edges of (NOT mono).  Equivalent: mark -1 iff all edges proper.
    #
    # We flag mono per edge into edge_flags via minterms, but only 4 flag ancillas
    # for 8 edges. So process edges in two batches of 4: compute 4 mono flags,
    # accumulate into a_edge (OR via: a_edge counts), but we need AND of NOT-mono
    # = NOT(OR of mono).  Use a_edge as running OR is hard to uncompute with phase
    # in middle. Instead: compute mono flag for each edge, and we want phase -1
    # when OR(mono)=0. Multi-controlled Z on all "NOT mono" = all edges proper.
    #
    # Plan: for each edge compute mono_e into its own persistent ancilla, but only
    # 4 ancillas. So we invert: compute proper_e = NOT mono_e is not needed as
    # separate; we do an MCX-style: we want to flip phase iff every edge proper,
    # i.e. every mono flag == 0.  Equivalent to multi-controlled-Z with all mono
    # flags as 0-controls. With only 4 flags we cannot hold all 8 simultaneously.
    #
    # Two-level approach: reduce 8 edges -> compute mono for edges, OR them all
    # into a_edge (a_edge = 1 iff any edge mono). Then phase -1 iff a_edge==0
    # (Z with 0-control). To OR into a_edge reversibly we compute each mono flag
    # then CX into a_edge then uncompute the flag -> a_edge accumulates OR? CX
    # accumulates XOR, not OR. But at most... not safe.
    #
    # Correct reversible OR-accumulation: use a_edge, and for each edge compute
    # mono_e into a fresh flag, then a_edge |= mono_e is not a single gate.
    # Instead accumulate the COUNT is also messy.
    #
    # Cleanest: compute mono_e for all 8 edges into 8 slots — but only 4+1.
    # Use the "toggle-detect" trick: We want MC-Z conditioned on all proper.
    # Build it as: compute mono_e into flag f_e (one at a time), NOT it to get
    # proper, but we need all simultaneously for the AND.
    #
    # Given constraints, use nested compute of a single AND accumulator with the
    # available 4 flags as scratch to build mono for 4 edges, control-transfer.
    # We implement the standard OR via De Morgan on a_edge:
    #   a_edge should become 1 iff any mono. Do it by: set a_edge=1, then for the
    #   ALL-proper case keep... simpler to directly do multi-0-control Z over the
    #   set of mono flags if we had them.
    #
    # We hold 4 mono flags at a time (batch), and reduce each batch of 4 into
    # a_edge as "batch has a mono edge" using OR built from the 4 flags, but OR of
    # 4 bits into a_edge reversibly = a_edge ^= OR(flags). We can compute OR(flags)
    # via: a_edge ^= NOT( AND(NOT f_i) ). Concretely:
    #   X on each flag (now flag_i = proper_i), then MCX(flags->a_edge) sets
    #   a_edge ^= AND(proper_i) = (all 4 proper). Undo X.
    # So per batch we get b = (all 4 edges proper). We want global AND of all 8
    # proper = b_batch0 AND b_batch1. Store each batch result in a separate slot.

    def compute_mono(u, v, f):
        # set f ^= [color(u)==color(v)]
        u0,u1 = qb(u); v0,v1 = qb(v)
        # color equal cases (u_code decode, v_code decode):
        # colors: c0={00,11}, c1={01}, c2={10}
        # EQ = (both in c0) OR (both ==01) OR (both ==10)
        # both ==01: u=01 and v=01
        # both ==10: u=10 and v=10
        # both in c0: u in{00,11} and v in{00,11}
        #
        # minterm both==01: u0&~u1 & v0&~v1
        qc.x(u1); qc.x(v1)
        qc.mcx([u0,u1,v0,v1], f)
        qc.x(u1); qc.x(v1)
        # both==10: ~u0&u1 & ~v0&v1
        qc.x(u0); qc.x(v0)
        qc.mcx([u0,u1,v0,v1], f)
        qc.x(u0); qc.x(v0)
        # both in c0 = (u==00 or u==11) and (v==00 or v==11)
        # u in c0 iff u0==u1 ; v in c0 iff v0==v1
        # (u0 XNOR u1) AND (v0 XNOR v1). Compute via cases: 00&00,00&11,11&00,11&11
        # u==00,v==00: ~u0~u1~v0~v1
        qc.x(u0);qc.x(u1);qc.x(v0);qc.x(v1)
        qc.mcx([u0,u1,v0,v1], f)
        qc.x(u0);qc.x(u1);qc.x(v0);qc.x(v1)
        # u==00,v==11: ~u0~u1 v0 v1
        qc.x(u0);qc.x(u1)
        qc.mcx([u0,u1,v0,v1], f)
        qc.x(u0);qc.x(u1)
        # u==11,v==00: u0 u1 ~v0~v1
        qc.x(v0);qc.x(v1)
        qc.mcx([u0,u1,v0,v1], f)
        qc.x(v0);qc.x(v1)
        # u==11,v==11: u0 u1 v0 v1
        qc.mcx([u0,u1,v0,v1], f)

    def uncompute_mono(u, v, f):
        u0,u1 = qb(u); v0,v1 = qb(v)
        qc.mcx([u0,u1,v0,v1], f)
        qc.x(v0);qc.x(v1)
        qc.mcx([u0,u1,v0,v1], f)
        qc.x(v0);qc.x(v1)
        qc.x(u0);qc.x(u1)
        qc.mcx([u0,u1,v0,v1], f)
        qc.x(u0);qc.x(u1)
        qc.x(u0);qc.x(u1);qc.x(v0);qc.x(v1)
        qc.mcx([u0,u1,v0,v1], f)
        qc.x(u0);qc.x(u1);qc.x(v0);qc.x(v1)
        qc.x(u0);qc.x(v0)
        qc.mcx([u0,u1,v0,v1], f)
        qc.x(u0);qc.x(v0)
        qc.x(u1);qc.x(v1)
        qc.mcx([u0,u1,v0,v1], f)
        qc.x(u1);qc.x(v1)

    batch0 = edges[:4]
    batch1 = edges[4:]
    f0, f1, f2, f3 = edge_flags  # scratch flags
    scratch = [f0, f1, f2, f3]

    # batch0 -> mono flags into f0..f3
    for (u,v), f in zip(batch0, scratch):
        compute_mono(u, v, f)
    # convert to proper (NOT mono)
    for f in scratch:
        qc.x(f)
    # a_edge ^= AND(proper of batch0) -> store into a_edge as batch0_all_proper
    qc.mcx(scratch, a_edge)
    # undo proper NOT and uncompute mono flags
    for f in scratch:
        qc.x(f)
    for (u,v), f in zip(batch0, scratch):
        uncompute_mono(u, v, f)

    # now a_edge = batch0_all_proper. Need to AND with batch1_all_proper for phase.
    # compute batch1 mono flags into f0..f3
    for (u,v), f in zip(batch1, scratch):
        compute_mono(u, v, f)
    for f in scratch:
        qc.x(f)
    # phase -1 iff a_edge==1 AND all four proper(batch1)==1
    qc.h(a_edge)
    qc.mcx(scratch + [a_edge], a_edge) if False else None
    qc.h(a_edge)
    # The above no-op placeholder removed; do proper multi-controlled Z:
    # phase -1 when a_edge=1 and scratch all 1  -> controlled-Z with controls
    # scratch and target a_edge (CZ symmetric): use H-MCX-H on a_edge.
    qc.h(a_edge)
    qc.mcx(scratch, a_edge)
    qc.h(a_edge)
    # undo batch1
    for f in scratch:
        qc.x(f)
    for (u,v), f in zip(batch1, scratch):
        uncompute_mono(u, v, f)

    # uncompute a_edge (redo batch0 computation to clear it)
    for (u,v), f in zip(batch0, scratch):
        compute_mono(u, v, f)
    for f in scratch:
        qc.x(f)
    qc.mcx(scratch, a_edge)
    for f in scratch:
        qc.x(f)
    for (u,v), f in zip(batch0, scratch):
        uncompute_mono(u, v, f)
