from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (3, 4)]

    def qb(v, bit):
        return problem_qubits[2 * v + bit]

    # For each edge we need a "different color" predicate.
    # Colors: c=0(00)->0, 1(01)->1, 2(10)->2, 3(11)->0.
    # color(u) != color(v)  <=>  NOT same_color(u,v).
    # We compute, per edge, an ancilla bit = same_color(u,v), and require
    # ALL same-bits == 0. Then f = AND over edges of (NOT same).
    #
    # same_color(u,v) with codes cu, cv, decode d(c) = c==3 ? 0 : c.
    # d values: 00->0, 01->1, 10->2, 11->0.
    # We encode decoded color as a 2-bit value equal to c except 11 mapped to 00.
    # Equivalently define indicator per color:
    #   isc0(c) = (c==00) or (c==11)
    #   isc1(c) = (c==01)
    #   isc2(c) = (c==10)
    # same_color(u,v) = OR over k of (isck(u) and isck(v)).
    #
    # We accumulate: mark states where SOME edge is monochromatic, i.e. f=1
    # means proper coloring => no edge monochromatic. So we want phase -1
    # when NO edge is monochromatic.
    #
    # Strategy: compute per-edge "bad" (same_color) into a shared scratch,
    # OR them into one flag, then phase on flag==0. But building a clean
    # uncomputable OR-of-ORs with a single ancilla per edge is cumbersome.
    #
    # Simpler correct approach: use one ancilla per edge? Only 5 ancillas,
    # 8 edges. Instead: compute each edge's "good" (different) predicate and
    # AND them all with a multi-controlled phase, using compute/uncompute
    # with a small reusable scratch via nested structure is hard.
    #
    # We use the following: since ancillas are limited (5), process by
    # computing per-vertex color indicators is expensive. Instead use a
    # sequential AND accumulator with a "clean flag" trick:
    #
    # Approach: build a big controlled operation. For each edge define the
    # boolean g_e = different(u,v). We want Z on the AND of all g_e.
    # We realize AND of all g_e as an mcp(pi) controlled on all g_e being 1,
    # by computing each g_e into its own ancilla... but 8 edges > 5 ancillas.
    #
    # Resolve: g_e = NOT same_e. same_e is OR of 3 AND-pairs. Compute same_e
    # into ancilla a0 (reused per edge), flip to g_e = NOT same_e (X on a0),
    # and fold g_e into an accumulator using a "count of failures" is complex.
    #
    # Cleanest: mark BAD (any monochromatic edge) then invert phase logic.
    # We instead directly implement: phase -1 iff all edges different.
    # Equivalent: phase -1 iff (number of monochromatic edges) == 0.
    #
    # We compute a single flag "any_bad" that is 1 if ANY edge monochromatic,
    # by OR-ing edge same-predicates into one ancilla flag, then apply phase
    # -1 conditioned on flag==0 (i.e. controlled on flag being 0), then
    # uncompute the flag.
    #
    # OR into a flag reversibly: flag starts 0. For each edge compute same_e
    # into scratch s (reused), then CX s->flag would OR-in but only correct
    # if we could uncompute s afterward WITHOUT disturbing flag; since s is
    # uncomputed right after copying into flag, and flag is monotone OR only
    # if same_e contributions don't overlap-cancel. CX accumulates XOR, not
    # OR. XOR != OR when two edges both monochromatic. So we need OR.
    #
    # Use a counter: incrementing flag on each bad edge and testing ==0 is
    # just OR via XOR-safe if we instead test the full multi-control on all
    # g_e (differents) = 1. AND of differents avoids the OR problem entirely.
    #
    # So: compute g_e = different(u,v) into ancilla b_e for each edge, then
    # multi-controlled-Z on all b_e, then uncompute. Need 8 ancillas but only
    # 5. Trick: reuse by computing differents in two passes is impossible for
    # a single AND. Instead nest: use a running AND accumulator.
    #
    # Running AND with 2 scratch + 1 accumulator:
    #   acc starts |1> (set X). For each edge: compute g_e into scratch s
    #   (and helper h), then acc' = acc AND g_e via Toffoli into a new acc?
    #   Needs alternating accumulators. With 5 ancillas we can do:
    #     a_scratch1, a_scratch2 (for computing g_e), and a chain acc0->acc1.
    #   We ping-pong acc between two ancillas, folding one edge at a time,
    #   uncomputing the older acc after each step.
    #
    # Implement AND accumulator ping-pong:
    scr = ancilla_qubits[0]   # scratch for same_color intermediate pair terms
    scr2 = ancilla_qubits[1]  # scratch for same_e (OR of pair terms)
    accA = ancilla_qubits[2]
    accB = ancilla_qubits[3]

    def compute_same(u, v, out):
        # out ^= same_color(u,v). out assumed 0 on entry.
        # same = isc0(u)&isc0(v) | isc1(u)&isc1(v) | isc2(u)&isc2(v)
        # These three pair-terms are mutually exclusive across colors of u?
        # Not necessarily: for fixed u, only one of isc0/1/2 can be... but
        # c=11 makes isc0 true (mapped color0). For a fixed code cu exactly
        # one indicator among isc0/isc1/isc2 is true (00->0,11->0 both give
        # isc0; 01->isc1; 10->isc2). So per vertex exactly one indicator.
        # Hence the three AND-pair terms are mutually exclusive => XOR == OR.
        # So we can safely CX/CCX-accumulate.
        #
        # isc1(c) = b0 & ~b1 ; isc2(c) = ~b0 & b1 ; isc0(c) = ~(isc1|isc2)
        #         = (b0&b1) | (~b0&~b1)  i.e. b0==b1.
        u0, u1 = qb(u, 0), qb(u, 1)
        v0, v1 = qb(v, 0), qb(v, 1)

        # term1: isc1(u)&isc1(v) = (u0&~u1)&(v0&~v1)
        # compute into scr the 4-input AND with negations on u1,v1.
        qc.x(u1); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], out)
        qc.x(u1); qc.x(v1)

        # term2: isc2(u)&isc2(v) = (~u0&u1)&(~v0&v1)
        qc.x(u0); qc.x(v0)
        qc.mcx([u0, u1, v0, v1], out)
        qc.x(u0); qc.x(v0)

        # term3: isc0(u)&isc0(v) = (u0==u1)&(v0==v1)
        # isc0(u) = u0==u1 : compute into scr, isc0(v) into scr2, then CCX.
        # scr,scr2 assumed 0 here (out is a separate ancilla).
        # isc0(u): set scr = ~(u0 xor u1) = 1 iff u0==u1.
        qc.cx(u0, scr); qc.cx(u1, scr); qc.x(scr)   # scr = NOT(u0^u1)
        qc.cx(v0, scr2); qc.cx(v1, scr2); qc.x(scr2)
        qc.ccx(scr, scr2, out)
        # uncompute scr, scr2
        qc.x(scr2); qc.cx(v1, scr2); qc.cx(v0, scr2)
        qc.x(scr); qc.cx(u1, scr); qc.cx(u0, scr)

    def uncompute_same(u, v, out):
        u0, u1 = qb(u, 0), qb(u, 1)
        v0, v1 = qb(v, 0), qb(v, 1)
        # mirror of compute_same in reverse order
        # term3 inverse
        qc.cx(u0, scr); qc.cx(u1, scr); qc.x(scr)
        qc.cx(v0, scr2); qc.cx(v1, scr2); qc.x(scr2)
        qc.ccx(scr, scr2, out)
        qc.x(scr2); qc.cx(v1, scr2); qc.cx(v0, scr2)
        qc.x(scr); qc.cx(u1, scr); qc.cx(u0, scr)
        # term2 inverse
        qc.x(u0); qc.x(v0)
        qc.mcx([u0, u1, v0, v1], out)
        qc.x(u0); qc.x(v0)
        # term1 inverse
        qc.x(u1); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], out)
        qc.x(u1); qc.x(v1)

    # AND accumulator over edges of g_e = NOT same_e.
    # acc holds product of g_e so far. Ping-pong accA/accB.
    # Initialize accA = 1 (empty AND identity).
    qc.x(accA)
    cur = accA
    nxt = accB
    n = len(edges)
    for idx, (u, v) in enumerate(edges):
        # compute same_e into scr2? scr2 is used inside compute_same; need a
        # dedicated same output. Use ancilla index 4 as same-bit.
        same = ancilla_qubits[4]
        compute_same(u, v, same)
        # g_e = NOT same
        qc.x(same)
        # nxt = cur AND g_e
        qc.ccx(cur, same, nxt)
        # uncompute g_e and same
        qc.x(same)
        uncompute_same(u, v, same)

        if idx == n - 1:
            # nxt now holds full AND = 1 iff proper coloring. Apply phase.
            qc.z(nxt)
            # uncompute nxt = cur AND g_e (recompute g_e)
            compute_same(u, v, same)
            qc.x(same)
            qc.ccx(cur, same, nxt)
            qc.x(same)
            uncompute_same(u, v, same)
            # uncompute cur chain below
        # uncompute cur for non-final steps happens after nxt established:
        # we must clear cur (the older accumulator) to reuse it next round.
        if idx < n - 1:
            # clear cur: recompute its defining AND from previous nxt? cur was
            # produced in prior iteration (or init). We instead keep cur set
            # and swap. To free the older ancilla we must uncompute it, but
            # cur's value depends on all prior edges. Simplest: don't free;
            # instead alternate and uncompute at the very end via reverse pass.
            cur, nxt = nxt, cur

    # Reverse pass: uncompute all intermediate accumulators back to clean,
    # including resetting accA (the initial X) — reverse the whole forward
    # accumulation except the phase.
    # Rebuild reverse: redo forward folds in reverse to clear.
    # After the loop, 'cur' points to the accumulator holding the final AND
    # (already phase-applied and uncomputed for the last step). We now unwind
    # earlier folds.
    # To keep this correct and self-inverse, redo the fold sequence in reverse.
    rev = list(enumerate(edges))[:-1][::-1]
    # Determine accumulator parity to unwind: replay swap logic in reverse.
    # Simpler robust unwind: mirror the exact forward operations (excluding
    # the final-step phase block) in reverse order.
    # Reconstruct forward op list for non-final steps and invert.
    # Since each non-final step did: compute g_e; ccx(cur,g,nxt); uncompute g;
    # swap. Inverting: for each such step in reverse, redo ccx(cur,g,nxt) to
    # clear nxt (Toffoli is self-inverse) with g recomputed.
    # Rebuild the cur/nxt pointer trajectory.
    ptr = [accA, accB]
    # forward trajectory
    c = accA; x = accB
    traj = []
    for idx, (u, v) in enumerate(edges):
        traj.append((idx, u, v, c, x))
        if idx < n - 1:
            c, x = x, c
    # unwind non-final steps in reverse
    for idx, u, v, cc, xx in reversed(traj[:-1]):
        same = ancilla_qubits[4]
        compute_same(u, v, same)
        qc.x(same)
        qc.ccx(cc, same, xx)   # clears xx back to 0 (self-inverse)
        qc.x(same)
        uncompute_same(u, v, same)
    # reset initial accA
    qc.x(accA)
