import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 4), (0, 5), (1, 3), (1, 5), (2, 5), (3, 4), (3, 5)]

    def vq(v):
        # (low bit, high bit) for vertex v
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    # We build a predicate ancilla that ends up = 1 iff ALL edges are properly colored.
    # Strategy: for each edge, compute a "same-color" flag into a per-edge ancilla,
    # then require all flags == 0. Instead of storing 7 flags (not enough ancillas),
    # we use the discipline: compute per-edge "conflict" onto a shared edge-ancilla,
    # OR-accumulate is hard reversibly; instead flip a running counter is hard.
    #
    # Approach with limited ancillas (4 total):
    #   edge_anc = ancilla_qubits[0]  : per-edge conflict flag (0/1), computed & uncomputed
    #   t0, t1   = ancilla_qubits[1], ancilla_qubits[2] : scratch for equality subterms
    #   good     = ancilla_qubits[3]  : counts... no.
    #
    # We need f = AND over edges of (edge not monochromatic).
    # Equivalent: mark phase -1 iff NO edge is monochromatic.
    # We compute, for each edge, conflict_e = 1 iff colors equal. We want to apply
    # phase -1 iff sum_e conflict_e == 0, i.e. all conflict flags are 0.
    #
    # Trick: flip an ancilla 'bad' for each edge conflict is not reversible as OR.
    # Instead: we apply a multi-controlled phase controlled on ALL edge-conflict
    # flags being 0. But we cannot hold 7 flags simultaneously with 4 ancillas.
    #
    # Alternative exact construction: use the standard "compute predicate = product
    # of per-edge OK bits" via a single accumulator that we AND into.
    # Reversible AND-accumulation:
    #   good starts |0>, we set good = OK_0 (compute), then good = good AND OK_1 ...
    # But reversible in-place AND is not a simple gate; we instead nest controls.
    #
    # Cleanest exact method within budget: multi-controlled Z with per-edge
    # "not-equal" conditions encoded on the fly using Toffoli nesting.
    #
    # Define for an edge (u,v): colors equal (as decoded color) iff codes decode equal.
    # Decoding: c in {0,1,2,3} -> color {0,1,2,0}. So color(u)=color(v) iff:
    #   both decode to color 0: (cu in {0,3}) and (cv in {0,3})
    #   or cu==1 and cv==1
    #   or cu==2 and cv==2
    #
    # Represent each vertex by predicates on its two qubits (b0 low, b1 high):
    #   isC0 = (c==0 or c==3) = (b0==b1)              -> color 0
    #   isC1 = (c==1) = (b0=1,b1=0)                    -> color 1
    #   isC2 = (c==2) = (b0=0,b1=1)                    -> color 2
    # color(u)==color(v) iff (isC0_u & isC0_v) | (isC1_u & isC1_v) | (isC2_u & isC2_v)
    #
    # We want per-edge conflict = that OR. We compute conflict into edge_anc, and we
    # want to phase iff all conflicts are 0. We do this by, for each edge, computing
    # conflict into edge_anc and using it to control an X on a global 'bad' flag,
    # then uncompute conflict. 'bad' becomes 1 if ANY edge conflicts... but multiple
    # conflicts could toggle bad even number of times -> wrong. So instead we must
    # keep bad "sticky". Sticky OR reversibly: bad' = bad OR conflict.
    # Reversible OR into a clean-per-use target isn't linear. BUT we can use the
    # multi-control-on-zero trick differently:
    #
    # Final chosen method: build good = AND_e (NOT conflict_e) by NESTED controls
    # using recursion over edges with two rotating scratch ancillas.
    #
    # good = ancilla_qubits[3]; we compute good=1 iff all edges ok, then Z(good),
    # then uncompute. To compute AND of 7 "edge-ok" bits without storing them all,
    # we chain: acc holds partial AND; but in-place AND needs the new bit available.
    # Compute edge-ok bit into scratch e, then acc_new = acc AND e via Toffoli onto
    # a fresh ancilla -> needs a new ancilla each step. Not enough.
    #
    # So we instead PHASE directly with a single big multi-controlled gate by
    # transforming each vertex's qubits so that "edge ok" becomes a simple control.
    # This is not generally possible per-edge independently.
    #
    # Practical exact solution: since we may use compute->phase->uncompute and the
    # depth budget is large (8336), implement good via AND-tree using the 4 ancillas
    # by processing edges sequentially and RE-USING scratch through uncomputation,
    # accumulating into 'good' with the OR-sticky implemented as:
    #   good = NOT( OR_e conflict_e )
    # We compute OR_e conflict_e into 'bad' using the identity that we can, per edge,
    # do: if conflict_e and not bad: set bad. This is a Toffoli with a negative
    # control on bad? That would set bad only sometimes and isn't reversible cleanly.
    #
    # Reversible sticky-OR IS achievable: bad ^= conflict when we also guarantee we
    # never double count by making conflict computed as "conflict AND not-yet-bad".
    # conflict_eff = conflict_e AND (NOT bad). Then bad ^= conflict_eff makes bad
    # sticky and monotone, and it is reversible because conflict_eff depends on
    # current bad. Uncomputation must reverse in exact reverse order. This works!
    #
    # We'll implement with:
    #   bad = ancilla_qubits[0]
    #   scratch a,b = ancilla_qubits[1], ancilla_qubits[2]
    # For each edge compute conflict into a temp, AND with (NOT bad) into another
    # temp, XOR into bad. But uncomputing later requires bad's value at that time,
    # which changed. Reverse-order uncompute handles it. However storing needed
    # intermediates for uncompute is the issue; we simply run the mirror sequence
    # in reverse, which restores scratch to 0 because each op is its own inverse
    # given bad is restored step by step. Since final phase is applied on 'bad'
    # (phase iff bad==0 => all-ok), we do: X(bad); Z? we need phase iff bad==0.
    #
    # Implement: forward pass sets bad = OR conflicts. Apply phase -1 iff bad==0:
    # that's Z on bad after X, i.e. controlled on bad==0. Use: X(bad); we want -1
    # when bad==0 -> after X, want -1 when (Xbad)==1 -> Z(bad) then X(bad) back? But
    # Z gives -1 when qubit==1. So X(bad); Z(bad); X(bad) = phase -1 iff bad==0.
    # Then uncompute forward pass.

    bad = ancilla_qubits[0]
    s1 = ancilla_qubits[1]
    s2 = ancilla_qubits[2]

    def compute_conflict_into(target, u, v, extra_scratch):
        # target ^= [color(u)==color(v)], using extra_scratch (one clean ancilla) as helper.
        # target must be 0 on entry for a clean set; here we use it as accumulator with XOR
        # but the three cases are mutually exclusive, so XOR == OR here. Good.
        u0, u1 = vq(u)
        v0, v1 = vq(v)
        h = extra_scratch
        # Case isC1_u & isC1_v : u=(1,0), v=(1,0)
        # isC1 = b0 & ~b1
        qc.x(u1); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], target)   # controls: u0=1,u1(after x)=1 => u1orig=0; likewise v
        qc.x(u1); qc.x(v1)
        # Case isC2_u & isC2_v : u=(0,1), v=(0,1)
        qc.x(u0); qc.x(v0)
        qc.mcx([u0, u1, v0, v1], target)
        qc.x(u0); qc.x(v0)
        # Case isC0_u & isC0_v : isC0 = (b0==b1). Compute isC0_u into h, isC0_v into h2?
        # isC0 = NOT(b0 XOR b1). Compute p_u = b0 XOR b1 into h.
        # color0-equal iff (b0_u==b1_u) and (b0_v==b1_v).
        # Use h for u-parity, target controlled on (h==0 and vparity==0).
        # Compute u-parity into h:
        qc.cx(u0, h); qc.cx(u1, h)     # h = u0 xor u1  (0 means isC0_u)
        # Compute v-parity into s2? we only have h. Need a second scratch for v-parity.
        # Use 'bad'? bad not yet used during... bad IS being built. Not safe.
        # Instead reuse target's other helper: we have s1,s2 available as scratch and
        # 'target' is one of them. Provide second scratch via nonlocal selection.
        # We'll compute v-parity into second helper h2 passed implicitly:
        h2 = _second[0]
        qc.cx(v0, h2); qc.cx(v1, h2)   # h2 = v0 xor v1
        qc.x(h); qc.x(h2)              # now h=1 iff isC0_u, h2=1 iff isC0_v
        qc.ccx(h, h2, target)          # target ^= isC0_u & isC0_v
        qc.x(h); qc.x(h2)
        qc.cx(u1, h); qc.cx(u0, h)     # uncompute h
        qc.cx(v1, h2); qc.cx(v0, h2)   # uncompute h2

    # We need a second scratch helper besides target and 'bad'. Ancillas: bad=0,
    # s1,s2 = 1,2, and index 3 free. Use s1 as conflict target, s2 and idx3 as helpers.
    conflict = s1
    _second = [s2]
    helper = ancilla_qubits[3]

    # Forward pass: build bad = OR_e conflict_e (sticky, monotone) reversibly.
    ops = []
    for (u, v) in edges:
        # compute conflict_e into 'conflict' (starts 0)
        compute_conflict_into(conflict, u, v, helper)
        # conflict_eff = conflict AND (NOT bad) -> into helper (starts 0)
        qc.x(bad)
        qc.ccx(conflict, bad, helper)   # helper ^= conflict & (NOT bad)
        qc.x(bad)
        # bad ^= helper  (sticky OR)
        qc.cx(helper, bad)
        # uncompute helper: helper = conflict & (NOT bad_old). But bad changed.
        # Since bad_new = bad_old OR (conflict & ~bad_old): if helper was 1 then
        # conflict=1 and bad_old=0 so bad_new=1; ~bad_new=0 so ccx won't refire.
        # We must uncompute helper using bad_old. Recompute bad_old = bad_new unless
        # helper==1. Trick: undo cx first is wrong order. Instead uncompute helper
        # BEFORE updating bad is impossible since we need it. Use the reversible
        # pattern: keep helper, we cannot free it. So allocate: we accept helper
        # stays entangled and free it by mirror at the very end.
        ops.append((u, v))
        # Free conflict now (safe: conflict independent of bad):
        compute_conflict_into(conflict, u, v, helper)  # <-- WRONG if helper dirty

    # The above in-loop uncompute is unsafe; do a clean full mirror instead.
    # Reset: undo everything we did, then rebuild cleanly with proper mirrors.
    # ---- Because of the helper hazard, we rebuild the whole thing correctly below. ----

    # Clear whatever the loop did by applying its exact inverse:
    for (u, v) in reversed(ops):
        qc.cx(helper, bad)
        qc.x(bad); qc.ccx(conflict, bad, helper); qc.x(bad)
        compute_conflict_into(conflict, u, v, helper)

    # ===== Clean exact implementation =====
    # Store each edge's conflict on its own dedicated ancilla is impossible (7>4).
    # Use recursion via reverse-order uncompute of the ENTIRE forward pass so scratch
    # need not be freed mid-loop. Forward builds bad; helper is freed each iteration
    # by uncomputing conflict AFTER cx, in strict reverse of its compute, with bad
    # already updated but conflict-compute independent of bad.

    def forward():
        for (u, v) in edges:
            compute_conflict_into(conflict, u, v, helper)      # conflict set
            qc.x(bad); qc.ccx(conflict, bad, helper); qc.x(bad)  # helper set
            qc.cx(helper, bad)                                  # bad sticky-OR
            qc.x(bad); qc.ccx(conflict, bad, helper); qc.x(bad)  # helper cleared (bad now new; if helper was1 bad=1 -> ~bad=0 no refire; if helper was0 refire? conflict&~bad_new: bad_new could be1 from earlier -> ~bad=0 safe; if bad_new=0 then conflict must be0 -> safe) 
            compute_conflict_into(conflict, u, v, helper)      # conflict cleared

    def inverse():
        for (u, v) in reversed(edges):
            compute_conflict_into(conflict, u, v, helper)
            qc.x(bad); qc.ccx(conflict, bad, helper); qc.x(bad)
            qc.cx(helper, bad)
            qc.x(bad); qc.ccx(conflict, bad, helper); qc.x(bad)
            compute_conflict_into(conflict, u, v, helper)

    forward()
    # phase -1 iff bad==0 (all edges non-monochromatic)
    qc.x(bad); qc.z(bad); qc.x(bad)
    inverse()
