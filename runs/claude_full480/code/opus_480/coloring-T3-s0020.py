from qiskit import QuantumCircuit
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Vertex v uses problem_qubits[2v] (b0, low) and problem_qubits[2v+1] (b1, high).
    # Code c = b0 + 2*b1; decode: c=3 -> color 0 (same as c=0).
    # Two vertices share a color iff their decoded colors are equal.
    #
    # Decoded color equality between vertices u,v (each a 2-bit code):
    #   colors equal iff (both codes decode to 0) OR (codes are exactly equal and in {1,2})
    # Let's characterize "same color" for two codes (a=(a0,a1), b=(b0,b1)):
    #   color(a)=0 iff a==00 or a==11  -> i.e. a0==a1
    #   color(a)=1 iff a==01           -> a0=1,a1=0
    #   color(a)=2 iff a==10           -> a0=0,a1=1
    # same color iff:
    #   both color0: (a0==a1) and (b0==b1)
    #   both color1: a0=1,a1=0,b0=1,b1=0
    #   both color2: a0=0,a1=1,b0=0,b1=1
    #
    # We want f(x)=1 iff for EVERY edge, colors DIFFER (no edge monochromatic).
    # Strategy: for each edge compute a "conflict" bit = 1 if endpoints share color.
    # f = 1 iff all conflict bits are 0. Use compute->phase->uncompute.
    #
    # We compute conflicts into an accumulator ancilla by an OR: we want to phase -1
    # only when NO edge conflicts. Equivalent: apply phase -1 iff AND over edges of
    # (not conflict_e). We build a flag ancilla that is 1 iff some edge conflicts,
    # then phase when flag==0.
    #
    # Concretely: use ancilla 'acc' initialized 0. For each edge, if conflict then
    # flip acc (but OR, not XOR). To get a true OR we use a controlled scheme; simpler:
    # compute each edge's conflict onto a fresh temp, but only 4 ancillas available.
    #
    # We instead accumulate: acc counts nothing; we need acc=1 iff ANY conflict.
    # Use multi-controlled toggles guarded so acc only goes 0->1 (OR via
    # controlling on acc being 0 is expensive). Instead use the standard trick:
    # phase = -1 iff product over edges of (no conflict). Compute per-edge
    # "ok_e" = NOT conflict is hard to AND for 7 edges with few ancillas.
    #
    # Simpler exact approach: mark conflicts additively into acc using the fact that
    # we only care whether acc==0 at the end. XOR-accumulation fails if two edges
    # conflict simultaneously (parity). So we must uncompute each conflict right after
    # OR-ing. Use a dedicated 'flag' ancilla and OR each conflict into it:
    #   OR(flag, c): flag ^= c AND (not flag). Implement OR via:
    #     compute conflict c into temp; then flag = flag OR temp using:
    #        x(flag) then ... -- messy.
    #
    # Cleanest robust method within budget: accumulate a COUNT of conflicts is unneeded.
    # Use De Morgan on the phase directly with an MCP (multi-controlled phase) that
    # fires only when all edges are non-conflicting. But "non-conflict" per edge is a
    # disjunction, not a single qubit.
    #
    # Therefore: compute one qubit per edge = conflict_e into 7 different ancilla slots?
    # Only 4 ancillas. So process edges sequentially, OR-ing into a single 'flag'
    # ancilla, using a second 'temp' ancilla for the current edge conflict, and OR via:
    #   flag <- flag OR temp, done reversibly by: ccx not enough for OR.
    # OR(flag,temp) reversible with clean flag path: we want at end flag = OR of all.
    # Implement OR incrementally as flag = NOT( (NOT flag) AND (NOT temp) ):
    #   x(flag); x(temp); ccx(flag_prev?...). This needs an extra target.
    #
    # We use 4 ancillas: a_flag, a_t0, a_t1, a_scratch.
    # For each edge we compute 'conflict' into a_t0 (reversibly, from problem qubits),
    # then merge into a_flag using OR with a_scratch as helper, then uncompute a_t0.
    #
    # OR merge (flag |= t) using one helper is done as:
    #   we maintain invariant a_flag = OR so far. To OR in t:
    #     new = flag OR t = flag XOR t XOR (flag AND t)
    #   Apply: ccx(flag,t,scratch)  # scratch = flag AND t   (scratch starts 0)
    #          cx(t,flag)           # flag ^= t
    #          cx(scratch,flag)     # flag ^= (flag_old AND t)
    #          # now flag = flag_old OR t ; but scratch still = flag_old AND t, must clear
    #   Clearing scratch: scratch = flag_old AND t. flag_old, t no longer both available
    #   cleanly. So instead compute scratch AFTER, or restructure. Use:
    #     cx(t,flag_tmp?) ... 
    # To keep it clean we compute OR into a NEW flag qubit each time -> too many.
    #
    # Given complexity, we use the parity-safe approach: uncompute each edge's conflict
    # immediately, and instead of OR, we directly do a multi-controlled phase per the
    # global condition by turning the whole thing into: phase -1 * (product of per-edge
    # (1 - 2*[conflict])?) -- not a clean diagonal of the right form.
    #
    # Final chosen method (exact, ancilla-safe): sequential OR with proper uncompute.
    a_flag = ancilla_qubits[0]
    a_t    = ancilla_qubits[1]
    a_s    = ancilla_qubits[2]

    edges = [(0,1),(0,4),(1,2),(1,3),(1,4),(2,4),(3,4)]

    def qb(v):
        return problem_qubits[2*v], problem_qubits[2*v+1]  # (b0, b1)

    # compute conflict(u,v) into target 't' (t assumed 0), using scratch-free construction.
    # same-color decomposition:
    #   both color0: (a0==a1) and (b0==b1)
    #   both color1: a0=1,a1=0,b0=1,b1=0
    #   both color2: a0=0,a1=1,b0=0,b1=1
    # conflict = both0 OR both1 OR both2.
    # We compute these three disjoint terms; they are mutually exclusive, so XOR = OR.
    # both1 term: t ^= a0 & ~a1 & b0 & ~b1
    # both2 term: t ^= ~a0 & a1 & ~b0 & b1
    # both0 term: (a0==a1)&(b0==b1). a0==a1 means NOT(a0 xor a1). This is not a simple
    #   AND of literals; it's (a0&a1)|(~a0&~b?)... handle via cases:
    #   both0 = [(a0&a1)|(~a0&~a1)] & [(b0&b1)|(~b0&~b1)]
    #   Expand into 4 mutually exclusive minterms over (a0,a1,b0,b1):
    #     (a0 a1 b0 b1), (a0 a1 ~b0 ~b1), (~a0 ~a1 b0 b1), (~a0 ~a1 ~b0 ~b1)
    # All 6 minterms total (4 for color0, 1 each for color1,color2) are mutually
    # exclusive, so XOR-ing each into t gives exactly conflict. Each minterm is a
    # 4-controlled X with appropriate polarities.
    def minterm(controls_pol, target):
        # controls_pol: list of (qubit, want1_bool)
        flips = [q for (q, want1) in controls_pol if not want1]
        for q in flips:
            qc.x(q)
        qc.mcx([q for (q, _) in controls_pol], target)
        for q in flips:
            qc.x(q)

    def compute_conflict(u, v, target):
        a0, a1 = qb(u)
        b0, b1 = qb(v)
        # color0 minterms (4)
        minterm([(a0,True),(a1,True),(b0,True),(b1,True)], target)
        minterm([(a0,True),(a1,True),(b0,False),(b1,False)], target)
        minterm([(a0,False),(a1,False),(b0,True),(b1,True)], target)
        minterm([(a0,False),(a1,False),(b0,False),(b1,False)], target)
        # color1 minterm: a0=1,a1=0,b0=1,b1=0
        minterm([(a0,True),(a1,False),(b0,True),(b1,False)], target)
        # color2 minterm: a0=0,a1=1,b0=0,b1=1
        minterm([(a0,False),(a1,True),(b0,False),(b1,True)], target)

    # OR-accumulate conflicts into a_flag using a_t (per-edge conflict) and a_s helper.
    # Invariant: a_flag holds OR of conflicts processed so far; a_t, a_s return to 0.
    def or_in(u, v):
        compute_conflict(u, v, a_t)           # a_t = conflict_e
        # a_flag <- a_flag OR a_t, with a_s helper, fully uncomputing a_s and a_t.
        qc.ccx(a_flag, a_t, a_s)              # a_s = flag & t
        qc.cx(a_t, a_flag)                    # flag ^= t
        qc.cx(a_s, a_flag)                    # flag ^= (flag_old & t) => flag = flag_old OR t
        # uncompute a_s: a_s = flag_old & t. flag now = flag_old OR t.
        # note flag_old & t == flag_new & t (since if t=1, flag_new=1). So a_s = flag & t.
        qc.ccx(a_flag, a_t, a_s)             # clears a_s
        # uncompute a_t back to 0
        compute_conflict(u, v, a_t)

    # Forward: build a_flag = OR of all edge conflicts.
    for (u, v) in edges:
        or_in(u, v)

    # Phase: we want -1 iff NO conflict, i.e. a_flag == 0.
    qc.x(a_flag)
    qc.z(a_flag)
    qc.x(a_flag)

    # Uncompute a_flag back to 0 by reversing the OR accumulation.
    def or_in_inverse(u, v):
        # exact inverse of or_in
        compute_conflict(u, v, a_t)          # recompute a_t = conflict_e (inverse of last step)
        qc.ccx(a_flag, a_t, a_s)             # reverse clears (rebuild a_s = flag & t)
        qc.cx(a_s, a_flag)
        qc.cx(a_t, a_flag)
        qc.ccx(a_flag, a_t, a_s)
        compute_conflict(u, v, a_t)

    for (u, v) in reversed(edges):
        or_in_inverse(u, v)
