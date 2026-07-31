from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1),(0,2),(0,3),(1,2),(1,3),(1,4),(2,4),(3,4)]

    def qbits(v):
        return problem_qubits[2*v], problem_qubits[2*v+1]

    # For each edge, ancilla e records "same color" (1 = monochromatic = bad).
    # Two vertices have the same decoded color iff:
    #   both codes are equal (00=00, 01=01, 10=10, 11=11), OR
    #   one code is 00 and other is 11 (both -> color 0), OR
    #   one code is 11 and other is 00.
    # Combined: same color iff (a0==b0 and a1==b1) OR (a1,a0)=(1,1)&(b1,b0)=(0,0)
    #           OR (a1,a0)=(0,0)&(b1,b0)=(1,1).
    # Equivalent: colorA == colorB where color = 0 if code in {00,11} else code.
    # Define for each vertex a 2-bit "canonical color" that maps 11->00.
    # canonical: t0 = b0 AND NOT(b0 AND b1)? Simpler: color index in {0,1,2}:
    #   c0 = b0 XOR (b0 AND b1)  -> 00->0,01->1,10->0,11->0
    #   c1 = b1 XOR (b0 AND b1)  -> 00->0,01->0,10->1,11->0
    # So canonical color bits (c1,c0): 00->00,01->01,10->10,11->00. Good.
    # Two vertices same color iff canonical bits equal.
    # Compute canonical color into 2 helper qubits? We only have 5 ancillas,
    # one per vertex is impossible alongside edge flags. Instead compute
    # canonical bits in place on the problem qubits reversibly, phase, undo.

    def to_canonical(v):
        b0, b1 = qbits(v)
        # c1 = b1 XOR (b0 AND b1) = b1 AND NOT b0
        # c0 = b0 XOR (b0 AND b1) = b0 AND NOT b1
        # Do it with a controlled swap-free transform:
        # if both b0,b1 ==1 -> set both to 0. That is: when b0&b1, flip both.
        qc.ccx(b0, b1, ancilla_qubits[0])   # temp = b0&b1
        qc.cx(ancilla_qubits[0], b0)
        qc.cx(ancilla_qubits[0], b1)
        qc.ccx(b0, b1, ancilla_qubits[0])   # uncompute temp?  invalid now

    # The in-place approach corrupts the temp uncompute because b0,b1 changed.
    # Use a clean standalone canonicalization per vertex with its own ancilla
    # as scratch, fully reversed after the edge phase block.

    n_edges = len(edges)

    def canon_forward(v, scratch):
        b0, b1 = qbits(v)
        qc.ccx(b0, b1, scratch)     # scratch = b0 AND b1
        qc.cx(scratch, b0)          # b0 -> b0 XOR (b0&b1)
        qc.cx(scratch, b1)          # b1 -> b1 XOR (b0&b1)
        # now (b0,b1) are canonical; scratch still = original b0&b1
        # but note: since 11 is the only case, canonical b0=b1=0 there.

    def canon_backward(v, scratch):
        b0, b1 = qbits(v)
        # invert: current canonical (b0,b1). If scratch==1 originally both were 1.
        qc.cx(scratch, b1)
        qc.cx(scratch, b0)
        qc.ccx(b0, b1, scratch)     # uncompute scratch (b0,b1 restored to orig)

    # Canonicalize all 5 vertices using 5 scratch ancillas.
    scratch = ancilla_qubits  # 5 scratch qubits, one per vertex
    for v in range(5):
        canon_forward(v, scratch[v])

    # Now every vertex holds canonical color bits. Edge monochromatic iff the
    # two 2-bit canonical codes are equal. f(x)=1 iff NO edge monochromatic.
    # Build phase: multiply -1 for good assignments (no monochromatic edge).
    #
    # We compute, per edge, an "equal" predicate and want to phase states where
    # ALL edges are unequal. Rather than allocate edge flags (no ancillas left),
    # use the identity with multi-controlled phase on the collective condition
    # via De Morgan is hard without flags. Instead phase the BAD set and note
    # f=1 is the complement; a global -1 minus phasing bad set gives complement
    # up to global phase only if bad-set phasing is the full predicate.
    #
    # Correct route: phase = -1 on good states. good = AND over edges of unequal.
    # Equality of two 2-bit codes (a0,a1),(b0,b1): eq = (a0==b0)&(a1==b1).
    # Reuse the freed problem-qubit structure: XOR b's onto a's to get diff bits,
    # then good = AND over edges of (OR of that edge's 2 diff bits), controlled
    # phase, then undo.

    # Represent per-edge inequality using the canonical bits directly with mcp.
    # For a single edge (u,w): unequal iff (u0 xor w0) OR (u1 xor w1).
    # AND over all edges of these ORs = good. This is a big AND-of-ORs; we can
    # apply a phase of -1 exactly on good states by: for each edge, temporarily
    # store equality into... we lack flags. So instead phase the complement:
    # Use inclusion via a single mcp over a constructed "all-unequal" control is
    # not directly a product of qubit controls (ORs), so we must materialize
    # each edge's equality bit. Reuse scratch AFTER canon by first undoing canon?
    # We keep canon; scratch qubits currently hold original b0&b1 (needed for
    # backward). We cannot reuse them. Therefore compute equality serially,
    # phasing bad states with sign-corrected multi-phase (Boolean expansion).

    # Practical correct method: mark BAD states (>=1 monochromatic edge) with
    # phase -1 is NOT equal to complement. So we instead directly realize the
    # good-state phase by a product of per-edge "unequal" multi-controlled
    # phases via the standard trick: apply H-Z-H style is overkill.
    #
    # Simplest exact construction that fits: since we already canonicalized,
    # detect each edge equality into one scratch bit AT A TIME, accumulate the
    # count of satisfied (unequal) edges into a single "all-good" flag using a
    # multi-controlled gate over per-edge equality bits computed sequentially
    # and immediately uncomputed is impossible (need them simultaneously).
    #
    # Given 5 free scratch already used, undo canon into originals first, then
    # reuse the SAME 5 ancillas as edge-equality storage for 5 of 8 edges and
    # the 2 code-qubits diff trick for the rest is fragile. To stay exact and
    # simple, we instead compute equality per edge onto a scratch, controlling
    # a running "bad" accumulation via OR into one dedicated flag, then phase.

    # --- Restart the phase logic cleanly using only reversible primitives. ---
    # Undo the canon we did above; redo with a scheme that leaves flags free.
    for v in reversed(range(5)):
        canon_backward(v, scratch[v])

    # Clean exact scheme:
    #  ancilla[0..4] reused as: for each edge compute eq bit, but we need all 8
    #  simultaneously -> only 5. So process good-flag by nesting:
    #  good = AND_e unequal_e. Compute nested using 1 flag + 1 temp:
    #    flag starts |1> via X. For each edge e: temp = equal_e; flag &= not temp
    #    i.e. if temp==1 (equal) -> flag=0. Realize: flag = flag AND (NOT temp).
    #    Use: X(temp); ccx(flag_prev...)? AND-accumulate needs another qubit.
    #  Use two ancillas as running AND with recompute-per-edge (temp reused),
    #  storing partial AND in a chain of 1 qubit is impossible reversibly in
    #  place. So allocate: a_flag = ancilla[0] (running good), a_tmp=ancilla[1],
    #  a_and=ancilla[2]. Standard reversible AND chain:
    a_good = ancilla_qubits[0]
    a_tmp  = ancilla_qubits[1]
    a_and  = ancilla_qubits[2]

    # canonicalize all vertices again, now using only... we need scratch per
    # vertex for canon, but canon_backward requires its scratch simultaneously
    # only during its own forward/backward, not across vertices. So we can
    # canonicalize one edge's two vertices, test, uncanonicalize, per edge,
    # using 2 scratch qubits, keeping a_good/a_tmp/a_and free.
    s0 = ancilla_qubits[3]
    s1 = ancilla_qubits[4]

    def edge_equal_into(u, w, target):
        # sets target ^= (canonical(u)==canonical(w))
        canon_forward(u, s0)
        canon_forward(w, s1)
        u0, u1 = qbits(u)
        w0, w1 = qbits(w)
        # diff bits onto u's qubits: u0 ^= w0 ; u1 ^= w1
        qc.cx(w0, u0)
        qc.cx(w1, u1)
        # equal iff u0==0 and u1==0  -> target ^= NOT u0 AND NOT u1
        qc.x(u0); qc.x(u1)
        qc.ccx(u0, u1, target)
        qc.x(u0); qc.x(u1)
        # undo diff
        qc.cx(w1, u1)
        qc.cx(w0, u0)
        canon_backward(w, s1)
        canon_backward(u, s0)

    # Build running good-flag = AND over edges of (unequal) = AND of (NOT equal).
    # Init a_good = 1.
    qc.x(a_good)
    # Chain: good_{k} = good_{k-1} AND (NOT equal_k).
    # Use a_and as next-good, a_tmp as equal bit.
    prev_good = a_good
    # We only have a_and as one extra AND-target, so alternate between a_good
    # and a_and as the running flag across edges.
    running = a_good
    other = a_and
    for e_idx, (u, w) in enumerate(edges):
        # compute equal into a_tmp
        edge_equal_into(u, w, a_tmp)
        # unequal = NOT equal
        qc.x(a_tmp)
        # other = running AND unequal
        qc.ccx(running, a_tmp, other)
        # uncompute a_tmp back to |0>: reverse
        qc.x(a_tmp)
        edge_equal_into(u, w, a_tmp)   # target^=equal again -> back to 0
        # swap roles: 'other' now holds new running good; must clear old running
        # but old running still entangled. Clean it: old running can be reset by
        # recomputing? It equals previous partial AND; uncompute later.
        running, other = other, running

    # After loop, 'running' holds good flag (=1 iff all edges unequal).
    # Apply phase.
    qc.z(running)

    # Uncompute the AND chain in reverse to return all ancillas to |0>.
    for e_idx in reversed(range(len(edges))):
        u, w = edges[e_idx]
        running, other = other, running
        edge_equal_into(u, w, a_tmp)
        qc.x(a_tmp)
        qc.ccx(running, a_tmp, other)
        qc.x(a_tmp)
        edge_equal_into(u, w, a_tmp)
    qc.x(a_good)
