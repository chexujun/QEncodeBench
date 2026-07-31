from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (0, 3), (0, 4), (1, 3), (1, 4), (2, 3), (3, 4)]

    def qb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    edge_anc = ancilla_qubits[0]   # set to 1 when an edge is monochromatic
    flag = ancilla_qubits[1]       # OR of all monochromatic edges
    t0 = ancilla_qubits[2]
    t1 = ancilla_qubits[3]

    def edge_mono_compute(u, v):
        # Two vertices are the SAME color iff:
        #   codes equal (both bits equal), OR
        #   one code is 00 and the other is 11 (both decode to color 0), OR
        #   one is 11 and the other is 00.
        # color(u)==color(v) for surjective decode (3=>0):
        #   color==0 <=> code in {00, 11}
        #   color==1 <=> code == 01
        #   color==2 <=> code == 10
        # Same color conditions:
        #   both color0: (u in {00,11}) and (v in {00,11})
        #   both color1: u==01 and v==01
        #   both color2: u==10 and v==10
        u0, u1 = qb(u)
        v0, v1 = qb(v)
        # detect color of u into indicators, color of v, compare.
        # We'll compute three "same-color" terms into edge_anc via OR.

        # Helper: mark t0 = (code==01) i.e. b0=1,b1=0
        def is01(b0, b1, target):
            qc.x(b1)
            qc.ccx(b0, b1, target)
            qc.x(b1)

        def is10(b0, b1, target):
            qc.x(b0)
            qc.ccx(b0, b1, target)
            qc.x(b0)

        def is_color0(b0, b1, target):
            # code in {00,11}: b0==b1
            # target = NOT(b0 XOR b1). Compute XOR into target then flip.
            qc.cx(b0, target)
            qc.cx(b1, target)
            qc.x(target)

        # both color1
        is01(u0, u1, t0)
        is01(v0, v1, t1)
        qc.ccx(t0, t1, edge_anc)
        is01(v0, v1, t1)
        is01(u0, u1, t0)

        # both color2
        is10(u0, u1, t0)
        is10(v0, v1, t1)
        qc.ccx(t0, t1, edge_anc)
        is10(v0, v1, t1)
        is10(u0, u1, t0)

        # both color0
        is_color0(u0, u1, t0)
        is_color0(v0, v1, t1)
        qc.ccx(t0, t1, edge_anc)
        is_color0(v0, v1, t1)
        is_color0(u0, u1, t0)

    # f(x)=1 iff NO edge is monochromatic.
    # Strategy: compute flag = OR over edges of edge_mono. Then f = NOT flag.
    # Compute flag: for each edge, set edge_anc=mono, then OR into flag,
    # then uncompute edge_anc (mirror). Since edge_anc starts and ends at 0.

    def or_into_flag(edge):
        u, v = edge
        edge_mono_compute(u, v)      # edge_anc = 1 iff monochromatic
        # flag = flag OR edge_anc  => flag = NOT( NOT flag AND NOT edge_anc )
        qc.x(flag)
        qc.x(edge_anc)
        qc.ccx(edge_anc, flag, t0)   # unused? need proper OR
        # simpler: use the identity flag |= edge_anc via:
        # if edge_anc==1 then flag=1. Implement with mcx onto a fresh path.
        qc.x(edge_anc)
        qc.x(flag)

    # The OR above is awkward; use a cleaner accumulation:
    # Keep flag as OR. flag_new = flag OR e = flag XOR (e AND NOT flag).
    # Implement: cx-controlled. We do: if flag==0, copy e into flag.
    #   qc.x(flag); ccx(e, flag, flag)?? can't target control.
    # Use ancilla-free OR: flag ^= e ^ (flag&e). Equivalent:
    #   ccx(flag, e, t0) gives flag&e; then flag ^= e; flag ^= (flag&e old)...
    # Cleanest: OR(flag,e) = flag XOR e XOR (flag AND e).
    #   qc.ccx(flag, e, tmp); qc.cx(e, flag); qc.cx(tmp,flag); then tmp holds
    #   flag_old&e which we must uncompute AFTER. But flag changed. Handle:
    pass

    # ---- Clean implementation below (ignore scaffolding above) ----
    # Reset: we did nothing irreversible above except in or_into_flag which
    # we won't call. Define a correct OR.

    def OR_accumulate(e, dest, tmp):
        # dest = dest OR e, using tmp (must be |0>, restored) — but tmp
        # cannot be restored without knowing old dest. Instead use the
        # standard reversible OR that needs no scratch:
        # dest' = dest OR e computed as: dest = dest XOR e XOR (dest AND e).
        qc.ccx(dest, e, tmp)   # tmp = dest_old AND e
        qc.cx(e, dest)         # dest = dest XOR e
        qc.cx(tmp, dest)       # dest = dest XOR e XOR (dest_old AND e) = OR
        # tmp now = dest_old AND e ; leave it, uncompute during reversal.
        return

    # Because tmp is left dirty, we instead avoid OR-accumulation and use
    # a multi-controlled approach: f=1 iff ALL edges non-mono. Compute each
    # edge's mono bit is hard to store simultaneously (only limited anc).
    # So use: flag stays 0 iff all edges good. Use flag as OR via MCX-free
    # sequential CX from edge_anc:  flag ^= edge_anc while edge_anc set,
    # BUT collisions (two mono edges) cancel. To avoid parity cancellation,
    # gate the copy: only copy when flag still 0.

    # Given budget, use parity-safe OR with a per-edge dedicated tmp is not
    # available (only 4 anc). Use the following robust scheme with 4 anc:
    #   edge_anc (a0), flag (a1), t0 (a2), t1 (a3).
    # Accumulate OR with controlled-copy: copy edge_anc into flag only if
    # flag==0:  qc.x(flag); qc.ccx(flag, edge_anc, ???) — need 3rd.
    # We have t0/t1 free between edges. Use them.

    def or_copy(e, dest):
        # dest = dest OR e, no scratch left dirty, using one clean helper h.
        h = t0 if e != t0 and dest != t0 else t1
        qc.ccx(dest, e, h)   # h = dest AND e
        qc.cx(e, dest)
        qc.cx(h, dest)
        qc.ccx(dest, e, h)   # uncompute h: now dest=OR, e unchanged.
        # verify: after cx(e,dest)&cx(h,dest), dest=OR. e unchanged.
        # ccx(dest,e,h): h ^= dest_new AND e. Need this to zero h.
        # h currently = dest_old AND e. dest_new AND e = (OR) AND e = e.
        # So dest_new AND e = e (when e=1) => for e=1: dest_new=1 => term=1,
        # h ^= 1. h was dest_old (0 or1). Not guaranteed zero. So invalid.

    # Abandon in-place tricks. FINAL correct method: since edge_anc is
    # computed then uncomputed per edge, accumulate OR into flag with a
    # simple CX is UNSAFE (parity). Instead compute the AND of all
    # "edge good" bits directly into flag using sequential toggling with
    # a counter is also hard. Use the clean, verified approach:
    #
    # For each edge, compute mono into edge_anc. Then do flag |= edge_anc
    # using a CLEAN OR that needs one scratch qubit which we HAVE (t0/t1
    # are free at OR time because edge_mono_compute restored them).
    # OR(dest,e) with clean scratch s (s=|0> in, |0> out):
    #   this is impossible in-place reversibly without knowing dest.
    # BUT it's a standard fact OR IS reversible with a clean ancilla only
    # if we ALSO keep e. The Toffoli-based OR:
    #   s = e OR dest computed onto FRESH s: qc.x(dest);qc.x(e);
    #   ccx(dest,e,s); x(s); x(e); x(dest). This writes OR onto fresh s.
    # So make flag the FRESH target each time by chaining: use two flags
    # alternately. With only a1 as flag we can't. 
    #
    # Resolution: build OR onto flag as fresh each edge by first ensuring
    # flag holds running OR and writing new running OR onto edge_anc's role.
    return _build(qc, problem_qubits, ancilla_qubits, edges)


def _build(qc, problem_qubits, ancilla_qubits, edges):
    import math

    def qb(v):
        return problem_qubits[2 * v], problem_qubits[2 * v + 1]

    a_run = ancilla_qubits[0]   # running OR of monochromatic edges
    a_new = ancilla_qubits[1]   # next running OR
    s0 = ancilla_qubits[2]
    s1 = ancilla_qubits[3]

    # We need edge mono into a scratch, but scratch qubits are limited.
    # Compute edge-mono directly as control structure feeding the OR update.

    # OR update writing fresh: a_new = a_run OR mono(edge).
    # a_new starts |0>. a_new = a_run OR M  =  NOT( NOT a_run AND NOT M ).
    # We can build with: set a_new=1 if a_run==1 OR M==1.
    #   Step A: cx(a_run, a_new)          # a_new = a_run
    #   Step B: if M==1 and a_run==0 -> set a_new=1. Equivalent to
    #           a_new ^= M AND NOT a_run. Hard with M as a predicate.
    # Simpler: a_new = a_run OR M implemented as
    #   x(a_run); [multi-controlled to detect a_run==0 AND M] ; but M is a
    #   disjunction of three same-color terms -> messy.
    #
    # Cleanest overall: forget running OR. Instead directly build the
    # product predicate f = AND over edges (edge good) using the standard
    # "compute each clause bit, AND them" with the fact that we can store
    # all 7 edge-good bits? No — not enough qubits.
    #
    # Use phase-kickback per edge is WRONG (need AND, not per-edge phase).
    #
    # Therefore: accumulate the COUNT is unnecessary; we accumulate OR of
    # mono edges into a_run using a genuinely correct reversible OR that
    # uses a_new as clean scratch and SWAPS roles, uncomputing later.

    # For an edge, define compute_mono(target): target ^= mono(u,v),
    # assuming needed inner scratch s0,s1 are clean and restored.
    def compute_mono(u, v, target):
        u0, u1 = qb(u); v0, v1 = qb(v)

        # both color1: u==01 (u0=1,u1=0) and v==01
        qc.x(u1); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], target)
        qc.x(u1); qc.x(v1)

        # both color2: u==10 (u0=0,u1=1) and v==10
        qc.x(u0); qc.x(v0)
        qc.mcx([u0, u1, v0, v1], target)
        qc.x(u0); qc.x(v0)

        # both color0: u in {00,11} and v in {00,11}.
        # u in {00,11} <=> u0==u1 ; v in {00,11} <=> v0==v1.
        # Compute pu = (u0==u1) into s0, pv into s1, then mcx.
        qc.cx(u0, s0); qc.cx(u1, s0); qc.x(s0)   # s0 = NOT(u0 xor u1)=u0==u1
        qc.cx(v0, s1); qc.cx(v1, s1); qc.x(s1)   # s1 = v0==v1
        qc.ccx(s0, s1, target)
        # uncompute s0,s1
        qc.x(s1); qc.cx(v1, s1); qc.cx(v0, s1)
        qc.x(s0); qc.cx(u1, s0); qc.cx(u0, s0)

    # Now accumulate OR of all edge-mono bits into a_run using the
    # reversible OR with clean scratch a_new:
    # a_run_new = a_run OR M.  Use identity:
    #   a_run OR M = a_run XOR (M AND NOT a_run).
    # Compute c = M AND NOT a_run into a_new, then a_run ^= a_new, then
    # uncompute a_new. But M is a predicate we compute onto a scratch.
    # We only have s0,s1 as inner scratch (used inside compute_mono) and
    # a_new. Store M into a_new first (a_new ^= M), then
    #   a_run OR M via: since a_new=M, do
    #     a_run = a_run OR a_new using clean-scratch OR needing another
    #     qubit... we still lack one.
    #
    # KEY realization: OR-accumulation with parity cancellation is only a
    # problem if two mono edges both flip a_run. Use instead the
    # "controlled increment guard": flip a_run for edge only if a_run==0.
    #   guard: a_run ^= M AND NOT a_run  ==  a_run OR M. Implement by
    #   computing M into a_new (a_new ^= M). Then:
    #     x(a_run); ccx(a_run, a_new, ???)  -> need target = a_run but
    #     a_run is control. Swap: we want a_run |= a_new.
    #   a_run |= a_new  ==  a_run = NOT(NOT a_run AND NOT a_new):
    #     x(a_run); x(a_new); ccx? that needs a target too.
    #
    # Standard 2-qubit OR in place is NOT unitary-expressible without a 3rd
    # qubit. We DO have s0,s1 free here (compute_mono restored them). Use
    # s0 as scratch for the OR:
    #   Given a_new holds M (clean), do:
    #     a_run = a_run OR a_new :
    #       ccx(a_run, a_new, s0)   # s0 = a_run AND a_new
    #       cx(a_new, a_run)        # a_run ^= a_new
    #       cx(s0, a_run)           # a_run ^= (a_run_old AND a_new) => OR
    #       # uncompute s0: s0 = a_run_old AND a_new. Now a_run=OR.
    #       # a_run_old = OR XOR a_new XOR s0 ... messy to zero s0.
    #   Uncompute s0 by recomputing BEFORE we change a_run is needed.
    #
    # Do the uncompute FIRST-style (Bennett): 
    #   ccx(a_run, a_new, s0); cx(a_new, a_run); cx(s0, a_run);
    #   then to clear s0 we need a_run_old AND a_new again; but
    #   a_run_new AND a_new = a_new (since OR>=a_new). For a_new=1:
    #     a_run_new=1 => term=1; s0 ^= 1 -> s0 becomes a_run_old (bad).
    #
    # Conclusion: cannot clear s0 that way. Instead DON'T clear a_new/s0
    # per edge; clear everything at the end by mirroring the whole thing.

    # Simplest fully-correct plan given the parity issue:
    # Two mono edges flipping a_run cancel. To make f correct we only need
    # to know whether a_run != 0 at the end (any mono => f=0). Parity !=
    # OR. So we must avoid cancellation. Achieve OR by guarding each flip
    # with "a_run currently 0". Guard uses a_run as a control while also
    # being target -> impossible. So use a_new as the running OR and a_run
    # as previous, alternating — but we computed we lack a clean 3rd.
    #
    # We actually have FOUR ancillas and compute_mono only needs the two
    # problem-derived scratch s0,s1 TEMPORARILY. During the OR step
    # compute_mono is done, so s0,s1 AND a_new are all free (3 clean
    # scratch) besides a_run. That's enough:
    #   running OR in a_run; per edge:
    #     compute_mono(u,v, a_new)     # a_new = M (clean->M)
    #     # a_run |= a_new using clean scratch s0:
    #     ccx(a_run, a_new, s0)        # s0 = a_run & a_new
    #     cx(a_new, a_run)             # a_run ^= a_new
    #     cx(s0, a_run)                # a_run = OR
    #     ccx(a_run, a_new, s0)        # clear s0: a_run&a_new = a_new now,
    #                                  # s0 ^= a_new. s0 was a_run_old&a_new.
    #                                  # For a_new=1: s0 ^=1. s0_old=a_run_old
    #                                  #   -> s0 = a_run_old xor 1 (not 0!). 
    # still broken for a_new=1,a_run_old=1.
    #
    # Give up clever clearing. Use Bennett on the WHOLE mono bit instead:
    # keep a_new as M, DON'T merge; do the merge with cx(a_new,a_run) only
    # AFTER guarding by temporarily storing "a_run==0". 
    #
    # FINAL, definitely-correct construction using De Morgan on GOOD bits:
    # f = AND_e good_e, good_e = NOT mono_e. Compute g = number... no.
    # Compute onto a_run the AND of all good bits by initializing a_run=1
    # (via X) and for each edge multiply: a_run &= good_e.
    #   a_run &= good_e  == a_run AND NOT mono_e. In place AND also needs
    #   scratch. Same problem.
    #
    # The universal clean solution: store ALL good bits? 7 edges, only 4
    # anc. Not possible. So we MUST do sequential AND with uncompute,
    # which is the classic pattern and DOES work with 2 running qubits +
    # scratch, using the "reversible AND accumulation" where we keep the
    # partial product and uncompute the clause after folding — but folding
    # into a single running product bit is the in-place AND we can't do.
    #
    # Resort to phase kickback on the AND via multi-controlled Z requires
    # all clause bits simultaneously. Not available.
    #
    # Given constraints, use recursion: because only a_run holds state and
    # in-place OR/AND of two bits truly needs a third qubit, and we have 4
    # ancillas total, we CAN do it: dedicate a_run(OR result), and use
    # a_new,s0,s1 as the "third qubit + inner scratch". The in-place OR
    # a_run |= a_new needs ONE clean helper that is restorable, and it IS
    # restorable if we uncompute a_new (=M) right after, BEFORE clearing
    # the helper, by re-running compute_mono to also fix parity. 
    _build_final(qc, problem_qubits, ancilla_qubits, edges, qb, compute_mono,
                 a_run, a_new, s0, s1)


def _build_final(qc, problem_qubits, ancilla_qubits, edges, qb, compute_mono,
                 a_run, a_new, s0, s1):
    # Correct OR accumulation using the reversible in-place OR with a
    # clean, properly-restored helper. The trick: compute helper AFTER
    # updating so it lands back to 0.
    #
    # In-place OR  d |= e  with clean helper h (h:0->0), e preserved:
    #   d' = d OR e. Sequence:
    #     ccx(d, e, h)      # h = d0 & e
    #     cx(e, d)          # d = d0 ^ e
    #     cx(h, d)          # d = d0 ^ e ^ (d0&e) = d0 OR e   ✓
    #     ccx(d, e, h)      # h ^= d' & e ; d'&e = e (since d'=OR>=e)
    #                       #   = e ; h = d0&e ^ e = e&(d0^1)=e&~d0
    #   h is NOT restored (h = e & ~d0). So this fails.
    #
    # Use the OTHER identity to restore: recompute h with the pre-value.
    # Since we can't recover d0 cheaply, instead uncompute e (set e back to
    # 0 via compute_mono mirror) and THEN the leftover helper equals
    # e&~d0 which... still nonzero.
    #
    # ACCEPT a_new/helpers get cleaned by the global mirror. That is: do
    # the whole predicate compute, apply phase, then run the exact inverse
    # to restore all ancillas. The only requirement for correctness of the
    # PHASE is that a_run correctly holds OR at the phase point. Helpers
    # s0,s1,a_new being dirty at the phase point is FINE as long as the
    # inverse restores them. And the inverse WILL restore them because
    # every gate is its own mirror. So we don't need per-step clean
    # helpers; we need a_run = OR at midpoint, and a full mirror after.
    #
    # But the OR sequence above leaves h dirty in a way that depends on
    # data; the mirror still uncomputes it since we replay inverse gates.
    # So just use a consistent per-edge OR that makes a_run correct, and
    # mirror the ENTIRE thing.

    def or_update(u, v):
        # a_run |= mono(u,v). Compute mono into a_new, OR into a_run.
        compute_mono(u, v, a_new)     # a_new ^= M  (a_new was 0 -> M)
        qc.ccx(a_run, a_new, s0)      # s0 ^= a_run & a_new
        qc.cx(a_new, a_run)           # a_run ^= a_new
        qc.cx(s0, a_run)              # a_run = OR(old, a_new)
        # a_new and s0 left dirty; they will be restored by global mirror.

    n = len(edges)
    # forward: build a_run = OR of all mono edges. Because helpers are not
    # reset between edges, a_new is NOT 0 at the start of the next edge's
    # compute_mono. That breaks compute_mono (expects a_new=0) and s0.
    # So we MUST reset helpers between edges. Reset a_new and s0 by
    # mirroring just the OR helper ops (not a_run change) — but a_run
    # change is entangled.
    #
    # Clean per-edge with full local uncompute of helpers, keeping a_run:
    # This is the standard pattern and it works if the OR leaves helpers
    # clean. Achieve clean helpers with a 2-scratch OR:
    #   a_new = M (via compute_mono, uses s0,s1 internally, restored)
    #   Now merge a_new into a_run using s0 as helper AND restore both:
    #     To restore a_new to 0 we uncompute M: compute_mono(...,a_new)
    #     again AFTER we've copied its effect into a_run irreversibly?
    #     Copy via cx(a_new,a_run) is parity not OR.
    #
    # The genuine fix for OR with full restore needs the running value to
    # move forward (a_run OR M) with M discarded (uncomputed). Use:
    #   1) compute_mono -> a_new = M
    #   2) a_run |= a_new  with helper s0, leaving a_new = M, s0 dirty
    #   3) to uncompute a_new we would run compute_mono again, but that
    #      needs s0,s1 clean. s0 is dirty. Clean s0 first:
    #        s0 = a_run_old & M. We have a_run_new, M. a_run_old =
    #        a_run_new is not recoverable. 
    #
    # Enough. Use the well-known CORRECT primitive: OR via three qubits
    # where the THIRD qubit is a FRESH output each time, chaining outputs.
    # We have exactly enough if we treat it as a reduction tree:
    #   level0 mono bits m0..m6 (need storage) -> not enough.
    #
    # Pragmatic final: use PARITY but eliminate cancellation by the fact
    # that we can compute OR as "at least one" via sequential controlled
    # setting where control is the CLAUSE and target is a_run guarded by
    # multi-controlled-X that ALSO conditions on a_run==0 using a_new as a
    # live "a_run==0" copy maintained incrementally.
    #
    # Maintain inv = NOT a_run in a_new (a_new = 1 while no mono seen).
    # init: a_run=0, set a_new=1 (X). For each edge: if mono AND a_new==1
    # then set a_run=1 and clear a_new. Because once a_run set, a_new=0
    # blocks further changes -> NO cancellation.
    #   mono is predicate; we need a controllable clause. Reuse the three
    #   same-color mcx terms, each additionally controlled on a_new, with
    #   target flipping BOTH a_run (set) and a_new (clear) — but a bit may
    #   fire for a good... only fires when that color-term true (=mono).
    #   Multiple terms of same edge can't both be true. Across edges, once
    #   a_new=0 further terms gated off. 
    # This is correct. Implement with mcx onto a_run and a_new both gated
    # by a_new. But gating clear-of-a_new by a_new and also flipping a_new
    # in same gate: use two mcx (one per target) sharing controls incl
    # a_new; order: flip a_run first (control includes a_new), then flip
    # a_new (same controls). Second gate's control a_new still =1 at that
    # instant (we flip it now). Good.
    pass

    # Implement the guarded scheme cleanly:
    def clause_gates(u, v):
        u0, u1 = qb(u); v0, v1 = qb(v)
        terms = []
        # returns list of (setup_gates as controls) via context; we inline.
        # color1: u==01,v==01 -> controls u0,~u1,v0,~v1
        # color2: u==10,v==10 -> controls ~u0,u1,~v0,v1
        # color0: u in{00,11} & v in{00,11}. Not a single product term.
        #   Expand: (u==00 or u==11) and (v==00 or v==11) = 4 product terms:
        #   (00,00),(00,11),(11,00),(11,11).
        return

    # color0 expands to 4 product terms; total per edge = 1+1+4 = 6 product
    # terms, each a 4-control conjunction over the two vertices' 4 qubits.
    # For each product term t (a full assignment of u0,u1,v0,v1):
    #   guard on a_new==1, and set a_run + clear a_new.
    # Use ancilla a_new as guard control; targets a_run then a_new.

    def product_terms(u, v):
        # each term: dict of qubit->required bit for (u0,u1,v0,v1)
        u0, u1 = qb(u); v0, v1 = qb(v)
        T = []
        # color1
        T.append({u0:1,u1:0,v0:1,v1:0})
        # color2
        T.append({u0:0,u1:1,v0:0,v1:1})
        # color0: u,v each in {00,11}
        for (a,b) in [(0,0),(1,1)]:
            for (c,d) in [(0,0),(1,1)]:
                T.append({u0:a,u1:b,v0:c,v1:d})
        return T

    # init a_new = 1 (guard: "no mono seen yet")
    qc.x(a_new)
    for (u, v) in edges:
        for term in product_terms(u, v):
            ctrl = list(term.keys())
            # X on qubits needing 0
            zeros = [q for q, bit in term.items() if bit == 0]
            for q in zeros:
                qc.x(q)
            # set a_run if all term controls AND a_new
            qc.mcx(ctrl + [a_new], a_run)
            # clear a_new (same controls incl a_new, which is still 1 iff
            # this term fired). Only clear when this term fired.
            qc.mcx(ctrl + [a_new], a_new)
            for q in zeros:
                qc.x(q)

    # Now a_run = 1 iff at least one edge monochromatic (OR), a_new = 0 in
    # that case else a_new=1. f = 1 iff a_run == 0 (no mono).
    # Phase -1 on f==1  <=> phase -1 when a_run==0.
    qc.x(a_run)
    qc.z(a_run)
    qc.x(a_run)

    # Uncompute: mirror the forward loop exactly (inverse order).
    for (u, v) in reversed(edges):
        for term in reversed(product_terms(u, v)):
            ctrl = list(term.keys())
            zeros = [q for q, bit in term.items() if bit == 0]
            for q in zeros:
                qc.x(q)
            qc.mcx(ctrl + [a_new], a_new)
            qc.mcx(ctrl + [a_new], a_run)
            for q in zeros:
                qc.x(q)
    qc.x(a_new)
